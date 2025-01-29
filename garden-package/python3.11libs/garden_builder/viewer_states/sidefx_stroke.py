# The code in this file was written by sidefx
# I, Parker Britt, have only made small modifications to make it work with my project

import hou
import math
import sys
import viewerstate.utils as su

class StrokeParams(object):
    """
    Stroke instance parameters. The class holds the stroke instance parameters
    as attributes for a given stroke operator and instance number.

    Parameters can be accessed as follows:

    params = StrokeParams(node, 55)
    params.colorr.set(red)
    params.colorg.set(green)
    etc...
    """
    def __init__(self, node, inst, param_prefix):
        self.inst = inst
        param_name = param_prefix + 'stroke' + str(inst)
        prefix_len = len(param_name) + 1

        def valid_parm(p):
            return p.isMultiParmInstance() and p.name().startswith(param_name)

        params = filter(valid_parm, node.parms())
        for p in params:
            self.__dict__[p.name()[prefix_len:]] = p


class StrokeData(object):
    """
    Holds the stroke data picked interactively

    Each point of the stroke is stored as a StrokeData.  This thus
    stores all the varying parameters of the stroke. Things that are
    constant over the entire stroke are stored in StrokeMetaData
    """
    VERSION = 2

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @staticmethod
    def create():
        return StrokeData(
            pos=hou.Vector3(0.0, 0.0, 0.0),
            dir=hou.Vector3(0.0, 0.0, 0.0),
            proj_pos=hou.Vector3(0.0, 0.0, 0.0),
            proj_uv=hou.Vector3(0.0, 0.0, 0.0),
            proj_prim=-1,
            proj_success=False,
            pressure=1.0,
            time=0.0,
            tilt=0.0,
            angle=0.0,
            roll=0.0,
        )

    def reset(self):
        self.pos=hou.Vector3(0.0, 0.0, 0.0)
        self.dir=hou.Vector3(0.0, 0.0, 0.0)
        self.proj_pos=hou.Vector3(0.0, 0.0, 0.0)
        self.proj_uv=hou.Vector3(0.0, 0.0, 0.0)
        self.proj_prim=-1
        self.proj_success=False
        self.pressure=1.0
        self.time=0.0
        self.tilt=0.0
        self.angle=0.0
        self.roll=0.0

    def encode(self):
        """
        Convert the data members to a hex string
        """
        stream = su.ByteStream()
        stream.add(self.pos, hou.Vector3)
        stream.add(self.dir, hou.Vector3)
        stream.add(self.pressure, float)
        stream.add(self.time, float)
        stream.add(self.tilt, float)
        stream.add(self.angle, float)
        stream.add(self.roll, float)
        stream.add(self.proj_pos, hou.Vector3)
        stream.add(self.proj_prim, int)
        stream.add(self.proj_uv, hou.Vector3)
        stream.add(self.proj_success, bool)
        return stream

    def decode(self, stream):
        pass


class StrokeMetaData(object):
    """
    Holds the meta data from the stroke state client node

    These are translated into primitive attributes by the Stroke SOP.
    The default behaviour if this state is to copy any stroke_ prefixed
    parameters into this meta data, but the buildMetaDataArray can
    be overridden to add additional information.
    """
    def __init__(self):
        self.name = None
        self.size = 0
        self.type = None
        self.value = None

    @staticmethod
    @su.trace
    def create(node, meta_data_array):
        """
        Creates an array of StrokeMetaData from the client node parameters and
        converts it to a json string
        """
        import json

        # insert number of total elements
        meta_data_array.insert(0, len(meta_data_array))

        if len(meta_data_array) == 1:
            meta_data_array.append({})

        return json.dumps(meta_data_array)

    @staticmethod
    def build_parms(node):
        """
        Returns an array of stroke parameters to consider for meta data
        """
        import parmutils

        def filter_tparm(t):
            """
            Filter out template parameters
            """
            prefix = 'stroke_'
            builtins = (
                'stroke_numstrokes',
                'stroke_radius',
                'stroke_opacity',
                'stroke_tool',
                'stroke_color',
                'stroke_projtype',
                'stroke_projcenter',
                'stroke_projgeoinput',
            )
            # Take all parms which start with 'stroke_' but are not builtin
            return t.name().startswith(prefix) and t.name() not in builtins

        g = node.parmTemplateGroup()

        return list(filter(filter_tparm, parmutils.getAllParmTemplates(g)))


class StrokeCursor(object):
    """
    Implements the brush cursor used by the stroke state. Also supports
    selection of different brush geometries.

    self.brushes should have a list of hou.Drawables that are available
    as brush cursors.
    """
    SIZE = 0.05
    COLOR = hou.Color(1.0, 0.0, 0.0)
    PROMPT = 'Left-drag to draw. Scroll mouse wheel or ctrl-shift-left-drag to resize brush.'
    BRUSH_NAMES = ('sphere', 'box', 'torus', 'tube')
    BRUSH_DISPLAY_MODES = {
        'brush_wireframe_display': hou.drawableDisplayMode.WireframeMode,
        'brush_viewport_display': hou.drawableDisplayMode.CurrentViewportMode,
    }
    BRUSH_PRIM_NAMES = ('sphere', 'circle', 'tube')
    BRUSH_PRIMS = {
        'sphere': hou.drawablePrimitive.Sphere,
        'circle': hou.drawablePrimitive.Circle,
        'tube': hou.drawablePrimitive.Tube,
    }
    POSITION_GEOMETRY = 0
    POSITION_SCREEN = 1

    @su.trace
    def __init__(self, scene_viewer, state_name, brush_name):
        self.scene_viewer = scene_viewer
        self.state_name = state_name

        # xform is our location in geometry space
        self.xform = hou.Matrix4(StrokeCursor.SIZE)

        # model_xform tracks the mapping from our geometry space
        # to the model space where we need to have the brush draw.
        self.model_xform = hou.Matrix4(1)

        # mouse_xform tracks the mapping from the mouse_dir
        # to the modeling space.
        self.mouse_xform = hou.Matrix4(1)

        # last_pos and resizing are used to handle resizing events
        self.last_pos = hou.Vector3()
        self.resizing = False

        # brushes is a list of all cursor geometries, which should
        # be hou.Drawables.  Caching these is preferred over recreating.
        self.brushes = []

        # position_type tracks where the cursor lives.  Geometry means
        # its coordinates are in the active geometry.  Screen means
        # they are in screen space.
        self.position_type = StrokeCursor.POSITION_GEOMETRY

        # orient_to_surface is whether the brush should orient its
        # z-axis to the hit position.  If there is no hit, it orients
        # to the screen direction.
        self.orient_to_surface = True

        # The prompt is drawn to the bottom of the viewport when the
        # cursor is active.
        self.prompt = StrokeCursor.PROMPT

        self.init_brushes()
        self.current_index = 0
        self.brush = self.brushes[self.current_index]

        # Controls if the cursor should be drawn or not.
        self.should_draw = True

        # Controls what projection type to use if it isn't a parameter
        # on the node.
        self.default_projtype = 0

        # Caches ray intersection caches
        self.raycache = hou.GeometryRayCache()

    def init_brushlist(self, list):
        """ Creates a brush primitive for each thing in the list,

            Each list element is (verb, param) where verb is a string
            for a hou.SopVerb and param is a dictionary to apply
            to the verb with .setParms.

            They are appended to self.brushes
        """
        sops = hou.sopNodeTypeCategory()
        for (name, parms) in list:
            verb = sops.nodeVerb(name)
            verb.setParms(parms)
            geo = hou.Geometry()
            verb.execute(geo, [])

            # add color and alpha attributes
            geo.addAttrib(hou.attribType.Vertex, "uv", (0,0))
            color_attrib = geo.addAttrib(hou.attribType.Prim, "Cd", (1.0, 1.0, 1.0))
            for prim in geo.prims():
                prim.setAttribValue(color_attrib, StrokeCursor.COLOR.rgb())

            # create a wireframe brush
            self.drawable_display = hou.drawableDisplayMode.WireframeMode
            brush = hou.SimpleDrawable(self.scene_viewer, geo, '%s_%s' % (self.state_name, name))
            brush.setDisplayMode(self.drawable_display)
            brush.setTransform(self.xform * self.model_xform)
            self.brushes.append(brush)

    def init_brushes(self):
        """ Creates a brush primitive for each name in BRUSH_NAMES
            They are appended to self.brushes
        """
        sops = hou.sopNodeTypeCategory()
        for name in StrokeCursor.BRUSH_NAMES:
            verb = sops.nodeVerb(name)
            geo = hou.Geometry()
            verb.execute(geo, [])

            # add color and alpha attributes
            geo.addAttrib(hou.attribType.Vertex, "uv", (0,0))
            color_attrib = geo.addAttrib(hou.attribType.Prim, "Cd", (1.0, 1.0, 1.0))
            for prim in geo.prims():
                prim.setAttribValue(color_attrib, StrokeCursor.COLOR.rgb())

            # create a shaded brush
            self.drawable_display = hou.drawableDisplayMode.WireframeMode
            brush = hou.SimpleDrawable(self.scene_viewer, geo, '%s_%s' % (self.state_name, name))
            brush.setDisplayMode(self.drawable_display)
            brush.setTransform(self.xform * self.model_xform)
            self.brushes.append(brush)

    def init_brushes_enum(self):
        """ Creates a brush primitive for each enum in BRUSH_PRIM_NAMES
            They are appended to self.brushes
        """
        for name in StrokeCursor.BRUSH_PRIM_NAMES:
            primt_type = StrokeCursor.BRUSH_PRIMS[name]
            self.drawable_display = hou.drawableDisplayMode.WireframeMode
            brush = hou.SimpleDrawable(self.scene_viewer, primt_type, '%s_%s' % (self.state_name, name))
            brush.setDisplayMode(self.drawable_display)
            brush.setTransform(self.xform * self.model_xform)
            self.brushes.append(brush)

    @su.trace
    def select_next(self):
        """ Cycles through the self.brushes updating the current
            self.brush.
        """
        if self.current_index+1 < len(self.brushes):
            index = self.current_index+1
        else:
            self.current_index = -1
            index = 0
        self.select(index)

    def brush_index(self, name):
        if name not in StrokeCursor.BRUSH_NAMES:
            raise ValueError
            return 0
        else:
            return StrokeCursor.BRUSH_NAMES.index(name)

    @su.trace
    def select(self, index):
        """ Sets the current self.brush from the self.brushes
        """
        if index == self.current_index:
            return

        if self.brush is not None:
            self.brush.enable(False)
            self.brush.show(False)

        self.current_index = index
        self.brush = self.brushes[index]
        self.brush.enable(True)
        self.brush.show(False)
        self.brush.setDisplayMode(self.drawable_display)

    @su.trace
    def show(self):
        self.brush.show(self.should_draw)

    @su.trace
    def hide(self):
        self.brush.show(False)

    @su.trace
    def enable(self):
        self.brush.enable(True)

    @su.trace
    def disable(self):
        self.brush.show(False)
        self.brush.enable(False)

    @su.trace
    def set_display_mode(self, value):
        self.drawable_display = StrokeCursor.BRUSH_DISPLAY_MODES[value]
        self.brush.setDisplayMode(self.drawable_display)

    @su.trace
    def update_xform(self, srt):
        """ Overrides the current transform with the given dictionary.
            The entries should match the keys of hou.Matrix4.explode.
        """
        # Our matrix may have become degenerate, likely soemone
        # getting us to zero scale, in which case explode fails.
        try:
            current_srt = self.xform.explode()
        except hou.OperationFailed:
            current_srt = { 'scale' : (0, 0, 0) }
        current_srt.update(srt)
        self.xform = hou.hmath.buildTransform(current_srt)
        self.brush.setTransform(self.xform * self.model_xform)

    @su.trace
    def update_model_xform(self, viewport):
        """ Update our model_xform from the selected viewport.  This
            will vary depending on our position type.
        """

        if self.position_type == StrokeCursor.POSITION_GEOMETRY:
            self.model_xform = viewport.modelToGeometryTransform().inverted()
            self.mouse_xform = hou.Matrix4(1.0)
        elif self.position_type == StrokeCursor.POSITION_SCREEN:
            vp = viewport
            self.model_xform = vp.windowToViewportTransform() * vp.viewportToNDCTransform() * vp.ndcToCameraTransform() * vp.cameraToModelTransform()
            self.mouse_xform = self.model_xform * vp.modelToGeometryTransform()
            self.mouse_xform = self.mouse_xform.inverted()


    @su.trace
    def update_position(self, node, mouse_point, mouse_dir, rad, intersect_geometry, geometry_xform=None):

        (cursor_pos, normal, uvw, prim_num, hit) = self.project_point(node, mouse_point, mouse_dir, intersect_geometry, geometry_xform=geometry_xform)

        if self.position_type == StrokeCursor.POSITION_GEOMETRY:
            if not self.resizing:
                self.last_pos = cursor_pos

            # Position is at the intersection point oriented to go along the normal
            srt = {
                'translate': (self.last_pos[0], self.last_pos[1], self.last_pos[2]),
                'scale': (rad, rad, rad),
                'rotate': (0, 0, 0),
            }

            if self.orient_to_surface:
                rotate_quaternion = hou.Quaternion()

                if hit and normal is not None:
                    rotate_quaternion.setToVectors(hou.Vector3(0, 0, 1), normal)
                else:
                    # no meaningful orientation obtainable, just orient to the screen
                    view_m = self.scene_viewer.curViewport().viewTransform().extractRotationMatrix3()
                    rotate_quaternion.setToRotationMatrix(view_m)

                rotate = rotate_quaternion.extractEulerRotates()
                srt['rotate'] = rotate

            self.update_xform(srt)

        elif self.position_type == StrokeCursor.POSITION_SCREEN:
            if not self.resizing:
                self.last_pos = mouse_point

            center = hou.Vector4(self.last_pos)
            center *= self.mouse_xform
            center /= center.w()
            rotate = (0, 0, 0)
            # We want it offset to avoid falling over the clipping plane.
            center[2] = -0.9999

            srt = {
                'translate': (center[0], center[1], center[2]),
                'scale': (rad, rad, rad),
                'rotate': rotate
            }

            self.update_xform(srt)


    @su.trace
    def project_point(self, node, mouse_point, mouse_dir, intersect_geometry, geometry_xform = None):
        """
        Performs a geometry intersection and returns a tuple with the intersection info:
        point: intersection point
        normal: intersection point normal
        uvw: parametric coordinates
        prim_num: intersection primitive number
        hit_success: return True if operation is successful or False otherwise
        """
        prim_num = -1
        uvw = hou.Vector3(0.0, 0.0, 0.0)

        proj_type = _eval_param(node, "stroke_projtype", self.default_projtype)

        hit = True
        if proj_type > 3:
            # Geometry-based projection.  Return true in Hit only if
            # we actually hit the geometry.  So we set it to False
            # as if we fall through we will be in a miss code path
            hit = False
            if intersect_geometry is not None:
                hit_point_geo = hou.Vector3()
                normal = hou.Vector3()

                temp_point = mouse_point
                temp_dir = mouse_dir
                if geometry_xform is not None:
                    temp_point = temp_point * geometry_xform.inverted()
                    temp_dir = temp_dir * geometry_xform.transposed()

                prim_num = self.raycache.intersect(intersect_geometry, temp_point, temp_dir, hit_point_geo, normal, uvw, 0, 1e18, 5e-3)
                if prim_num >= 0:
                    if geometry_xform is not None:
                        hit_point_geo *= geometry_xform

                        if normal is not None:
                            normal *= geometry_xform.transposed().inverted()

                    return (hit_point_geo, normal, uvw, prim_num, True)

        # We include screen projection in the first case so it consistently
        # uses the provided projection center.
        if proj_type <= 3:
            # One of the pre-set projection axes.
            proj_center = _eval_param_v3(node, "stroke_projcenterx", "stroke_projcentery", "stroke_projcenterz", (0, 0, 0))
            proj_dir = _projection_dir(proj_type, mouse_dir)
        else: 
            # Geometry projection.  
            # We try to fit a plane to our last hit position and
            # the current mouse direction.  If in POSITION_SCREEN this
            # will be the last mouse position on the near plane.  If
            # POSITION_GEOMETRY this is the cursor's last center position.
            proj_center = self.last_pos
            proj_dir = mouse_dir

        # Compute ray-plane intersection
        tnum = proj_dir.dot(proj_center - mouse_point)
        tdenom = proj_dir.dot(mouse_dir)
        if (tnum > 0 and tdenom > 0) or (tnum < 0 and tdenom < 0):
            hit_point_plane = mouse_point + tnum / tdenom * mouse_dir
        else:
            # Ray does not intersect plane (or lays on the plane)
            hit = False
            hit_point_plane = hou.Vector3()

        return (hit_point_plane, None, uvw, prim_num, hit)

    @su.trace
    def show_prompt(self):
        self.scene_viewer.setPromptMessage(self.prompt)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
@su.trace
def _eval_param(node, param, default):
    """ Evaluates param on node, but if it doesn't exist just
        silently return default.
    """
    try:
        return node.evalParm(param)
    except:
        return default

@su.trace
def _eval_param_v3(node, param1, param2, param3, default):
    """ Evaluates vector3 param on node, but if it doesn't exist just
        silently return default.
    """
    try:
        return hou.Vector3(
            node.evalParm(param1), node.evalParm(param2), node.evalParm(param3))
    except:
        return hou.Vector3(default)

@su.trace
def _eval_param_c(node, param1, param2, param3, default):
    """ Evaluates color param on node, but if it doesn't exist just
        silently return default.
    """
    try:
        return hou.Color(
            node.evalParm(param1), node.evalParm(param2), node.evalParm(param3))
    except:
        return hou.Color(default)

@su.trace
def _projection_dir(proj_type, screen_space_projection_dir):
    """ Convert the projection menu item into a geometry
        projection direction.
    """
    if proj_type == 0:
        return hou.Vector3(0, 0, 1)
    elif proj_type == 1:
        return hou.Vector3(1, 0, 0)
    elif proj_type == 2:
        return hou.Vector3(0, 1, 0)
    else:
        return screen_space_projection_dir

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

class StrokeState(object):
    """
    Stroke state implementation to handle the mouse/tablet interaction.

    You can subclass the StrokeState to further customize the behaviour
    of the interaction.
    """
    CURSOR_DRAG_FACTOR = 0.1

    @su.trace
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.strokes = []
        self.strokesMirrorData = []
        self.strokesNextToEncode = 0
        self.mouse_point = hou.Vector3()
        self.mouse_dir = hou.Vector3()
        self.stopwatch = su.Stopwatch()
        self.epoch_time = 0
        self.stroke_cancelled = False

        # meta_data_params is a cache for which parameters to copy
        # to the metadata.
        self.meta_data_parms = None

        # If enabled, using the shift key and dragging will engage
        # the drag logic.  Disable to allow the shift modifier to
        # be used for normal strokes
        self.enable_shift_drag_resize = True

        # capture_parms are any extra keys that should be passed from
        # the kwargs of the event callbacks to the stroke-specific
        # event callbacks.
        self.capture_parms = []

        # Caches the current geometry to intersect with.  Override
        # intersectGeometry to change from the default of using the
        # first input.
        self.intersect_geometry = None

        # The cursor provides in-viewport visualization of where the
        # stroke is actively locating.
        self.cursor = StrokeCursor(self.scene_viewer, self.state_name, 'sphere')

    def onPreStroke(self, node, ui_event, captured_parms):
        """ Called when a stroke is started.

            Override this to setup any stroke_ parameters.
        """
        su.triggerParmCallback("prestroke", node, ui_event.device())

    def onPostStroke(self, node, ui_event, captured_parms):
        """ Called when a stroke is complete

            Override this to finish strokes.  This is often used
            to copy strokes into an explicit cache.
        """
        su.triggerParmCallback("poststroke", node, ui_event.device())

    def onPreApplyStroke(self, node, ui_event, captured_parms):
        """ Called before new stroke values are copied.  This is done
            during the stroke operation.

            Override this to do any preparation just before the stroke
            parameters are updated for an active stroke.
        """
        pass

    def onPostApplyStroke(self, node, ui_event, captured_parms):
        """ Called before after new stroke values are copied.  This is done
            during the stroke operation.

            Override this to do any clean up for every stroke
            update.  This can be used to break up a single stroke
            into a series of operations, for example.
        """
        pass

    def onPreMouseEvent(self, node, ui_event, captured_parms):
        """ Called at the start of every mouse event.

            Warning: This is outside of undo blocks, so do not
            set parameters without handling undos.

            Override this to inject code just before all mouse event
            processing
        """
        pass

    def onPostMouseEvent(self, node, ui_event, captured_parms):
        """ Called at the end of every mouse event.

            Warning: This is outside of undo blocks, so do not
            set parameters without handling undos.

            Override this to inject code just after all mouse event
            processing
        """
        pass

    def buildMetaDataArray(self, node, ui_event, captured_parms, mirrorxform):
        """ Returns an array of dictionaries storing the metadata
            for the stroke.  This is encoded as JSON and put in
            the stroke metadata parameter.  Base behaviour is to
            encode all stroke_ prefixed parms.
            mirrorxform is the current mirroring transform being
            written out.

            Override this to add metadata without the need to
            make stroke_ parameters.
        """
        convertible_to_int = (
            hou.parmTemplateType.Toggle,
            hou.parmTemplateType.Menu,
        )

        meta_data_array = []
        for p in self.meta_data_parms:
            name = p.name()
            data_type = p.type()

            meta_data = StrokeMetaData()
            meta_data.size = 1
            meta_data.name = name

            if data_type == hou.parmTemplateType.Float:
                values = node.evalParmTuple(name)
                meta_data.type = "float"
                meta_data.size = len(values)
                meta_data.value = " ".join(map(str, values))
            elif data_type == hou.parmTemplateType.Int:
                values = node.evalParmTuple(name)
                meta_data.type = "int"
                meta_data.size = len(values)
                meta_data.value = " ".join(map(str, values))
            elif data_type == hou.parmTemplateType.String:
                meta_data.type = "string"
                meta_data.value = node.evalParm(name)
            elif data_type in convertible_to_int:
                meta_data.type = "int"
                meta_data.value = str(node.evalParm(name))
            else:
                continue

            meta_data_array.append(meta_data.__dict__)
        return meta_data_array

    def onEnter(self, kwargs):
        """ Called whenever the state begins.

            Override this to perform any setup, such as visualizers,
            that should be active whenever the state is.
        """
        # update the cursor with the current stroke radius
        node = kwargs['node']
        rad = _eval_param(node, self.radiusParmName(node), StrokeCursor.SIZE)
        self.cursor.update_xform({'scale': (rad, rad, rad)})
        self.cursor.hide()
        self.cursor.enable()

        # pre-build a list of meta data parameters from the node
        self.meta_data_parms = StrokeMetaData.build_parms(node)

        self.cursor.show_prompt()

    def onExit(self, kwargs):
        """ Called whenever the state ends.

            Override this to perform any cleanup, such as visualizers,
            that should be finished whenever the state is.
        """
        su.Menu.clear()

    def onMouseEvent(self, kwargs):
        """ Called whenever the mouse moves in the viewport and
            the state is active.

            This callback should ideally not need to be overridden
            and instead the various hooks overidden instead to get
            custom behaviour.
        """
        ui_event = kwargs['ui_event']
        node = kwargs['node']

        captured_parms = {key: kwargs.get(key, None) for key in self.capture_parms}

        self.onPreMouseEvent(node, ui_event, captured_parms)

        # real time mode ?
        realtime_mode = kwargs['realtime_mode']

        # store ray coordinates for the geometry intersection
        (self.mouse_point, self.mouse_dir) = ui_event.ray()

        # compute position only if no device events are in the queue
        if not ui_event.hasQueuedEvents():
            self.cursor.update_model_xform(ui_event.curViewport())
            self.cursor.update_position(node, self.mouse_point, self.mouse_dir, _eval_param(node, self.radiusParmName(node), StrokeCursor.SIZE), self.intersectGeometry(node))

        started_resizing = False
        # If ctrl-shift-drag to resize is on, and both shift and ctrl are pressed, start resizing
        if self.enable_shift_drag_resize and ui_event.reason() == hou.uiEventReason.Start and ui_event.device().isShiftKey() and ui_event.device().isCtrlKey():
            self.cursor.resizing = True
            started_resizing = True
            self.cursor.last_mouse_x = ui_event.device().mouseX()
            self.cursor.last_mouse_y = ui_event.device().mouseY()

        if self.cursor.resizing:
            self.handleResize(node, ui_event, started_resizing)
            self.cursor.show()
            self.onPostMouseEvent(node, ui_event, captured_parms)
            return

        if ui_event.reason() == hou.uiEventReason.Start or ui_event.reason() == hou.uiEventReason.Picked:

            # opens an undo block for the draw stroke operation
            self.cursor.scene_viewer.beginStateUndo('Draw Stroke')

            self.onPreStroke(node, ui_event, captured_parms)

            self.reset_active_stroke()
            if realtime_mode and ui_event.reason() == hou.uiEventReason.Start:
                self.apply_stroke(kwargs, ui_event, False, captured_parms) # MODIFIED

        if ui_event.reason() == hou.uiEventReason.Start or \
            ui_event.reason() == hou.uiEventReason.Picked or \
            ui_event.reason() == hou.uiEventReason.Active or \
            ui_event.reason() == hou.uiEventReason.Changed:

            self.handle_stroke_event(ui_event, node)

        if ui_event.reason() == hou.uiEventReason.Changed or \
            ui_event.reason() == hou.uiEventReason.Picked:

            self.apply_stroke(kwargs, ui_event, realtime_mode, captured_parms) # MODIFIED
            self.reset_active_stroke()

            self.onPostStroke(node, ui_event, captured_parms)

            # closes the current undo block for the draw stroke operation
            self.cursor.scene_viewer.endStateUndo()

        elif realtime_mode and ui_event.reason() == hou.uiEventReason.Active:
            if not ui_event.hasQueuedEvents():
                self.apply_stroke(kwargs, ui_event, realtime_mode, captured_parms) # MODIFIED

        self.cursor.show()

        self.onPostMouseEvent(node, ui_event, captured_parms)

    def onMouseWheelEvent(self, kwargs):
        """ Called whenever the mouse wheel moves.

            Default behaviour is to resize the cursor.

            Override this to do different things on mouse wheel.
        """
        ui_event = kwargs['ui_event']
        node = kwargs['node']
        dist = ui_event.device().mouseWheel()
        dist *= 10.0

        if ui_event.device().isShiftKey() is True:
            dist *= StrokeState.CURSOR_DRAG_FACTOR

        self.resize_cursor(node, dist)

    def onResume(self, kwargs):
        """ Called whenever the state is resumes from an interruption,
            such as by switching back from a volatile state.
        """
        self.cursor.show()
        self.cursor.show_prompt()

    def onInterrupt(self, kwargs):
        """ Called whenever the state is temporary interrupted,
            such as by switching to a volatile state.
        """
        self.cursor.hide()

    def onDraw(self, kwargs):
        """ Called every time the viewport renders.

            Override to render custom guide geometry.
        """
        pass

    def onMenuAction(self, kwargs):
        """ Called when a state menu is selected.

            Override this to handle your own menu items.
        """
        menu_item = kwargs['menu_item']
        node = kwargs['node']
        if menu_item == 'cycle_brushes':
            self.cursor.select_next()
            self.cursor.update_position(node, self.mouse_point, self.mouse_dir, _eval_param(node, self.radiusParmName(node), StrokeCursor.SIZE), self.intersectGeometry(node))
            self.cursor.show()
        elif menu_item == 'brush_display_mode':
            self.cursor.set_display_mode(kwargs['brush_display_mode'])

    def radiusParmName(self, node):
        """ Returns the name of the parameter to use for determining the
            current radius of the brush.

            Override this to allow multiple radius parameters.
        """
        return 'stroke_radius'

    def updateIntersectGeometry(self, isectnode):
        """ Update self.intersect_geometry to use geometry
            from isectnode
        """
        if self.intersect_geometry is None:
            self.intersect_geometry = isectnode.geometry()
        else:
            # Check to see if we have already cached this.
            if self.intersect_geometry.sopNode() != isectnode:
                self.intersect_geometry = isectnode.geometry()

    def intersectGeometry(self, node):
        """ Returns the geometry to use for intersections of the ray.
            It is important that this is cached to avoid regenerating
            the intersection table.  In particular, the hou.Geometry
            object must be cached, two objects pointing to the
            same node will not share the intersection cache!

            Override this to allow drawing on geometry other than
            the first input.
        """
        proj_type = _eval_param(node, "stroke_projtype", self.cursor.default_projtype)

        if proj_type > 3:
            if node.inputFollowingOutputs(0) is not None:
                isectnode = node.inputFollowingOutputs(0)
                self.updateIntersectGeometry(isectnode)
            else:
                self.intersect_geometry = None
        return self.intersect_geometry

    @su.trace
    def activeMirrorTransforms(self, node):
        """ Returns a list of active transforms to mirror the
            incoming strokes with.  These should be hou.Matrix4.
            The first should be identity to represent passing through.
            If an empty list, no strokes will be recorded.

            Override this to add mirror transforms.
        """
        result = hou.Matrix4()
        result.setToIdentity()
        return [ result ]

    def handleResize(self, node, ui_event, started_resizing):
        """ Uses resize_cursor to adjust stroke radius according to
            a mouse drag event.

            Used internally.
        """
        mouse_x = ui_event.device().mouseX()
        mouse_y = ui_event.device().mouseY()

        dist = 0
        dist += -self.cursor.last_mouse_x + mouse_x
        dist += -self.cursor.last_mouse_y + mouse_y

        self.cursor.last_mouse_x = mouse_x
        self.cursor.last_mouse_y = mouse_y

        if started_resizing:
            # opens an undo block for the brush operation
            self.cursor.scene_viewer.beginStateUndo('Brush Resize')
            pass

        self.resize_cursor(node, dist)

        if ui_event.reason() == hou.uiEventReason.Changed:
            # closes the current brush undo block
            self.cursor.resizing = False
            self.cursor.scene_viewer.endStateUndo()

    @su.trace
    def resize_cursor(self, node, dist):
        """ Adjusts the current stroke radius by a requested bump.

            Used internally.
        """
        scale = pow(1.01, dist)
        stroke_radius = node.parm(self.radiusParmName(node))
        if stroke_radius is None: # If we have no radius parm, just do nothing
            return
        rad = stroke_radius.evalAsFloat()
        rad *= scale
        stroke_radius.set(rad)
        self.cursor.update_xform({'scale': (rad, rad, rad)})

    @su.trace
    def bytes(self, mirrorData):
        """ Encodes the list of StrokeData as an array of bytes and
            returns in a fashion the Stroke SOP expects.

            Used internally.
        """
        stream = su.ByteStream()
        stream.add(StrokeData.VERSION, int)
        stream .add(len(self.strokes), int)
        stream.add(mirrorData, su.ByteStream)
        return stream.data().decode()

    @su.trace
    def reset_active_stroke(self):
        """ Clears any active stroke.
        """
        self.strokes = []
        self.strokesMirrorData = []
        self.strokesNextToEncode = 0

    @su.trace
    def cancel_active_stroke(self):
        """ Clears active stroke and sets a flag to stop processing so
            the node won't be dirtied.   
            This is valid only in onPreApplyStroke.
        """
        self.reset_active_stroke()
        self.stroke_cancelled = True

    @su.trace
    def apply_stroke(self, kwargs, ui_event, update, captured_parms):
        """ Updates the stroke multiparameter from the current
            self.strokes information.

            Used internally.
        """
        node = kwargs["parm_node"]
        stroke_numstrokes_param = node.parm(kwargs["stroke_num_parm_name"]) # MODIFIED
        param_prefix = kwargs["param_prefix"]

        self.stroke_cancelled = False

        # Performs the following as undoable operations
        with hou.undos.group("Draw Stroke"):
            self.onPreApplyStroke(node, ui_event, captured_parms)

            # The pre-apply may have reset our strokes so
            # we exit early.
            if self.stroke_cancelled:
                return

            stroke_numstrokes = stroke_numstrokes_param.evalAsInt()
            stroke_radius = _eval_param(node, self.radiusParmName(node), StrokeCursor.SIZE)
            stroke_opacity = _eval_param(node, 'stroke_opacity', 1)
            stroke_tool = _eval_param(node, 'stroke_tool', -1)
            stroke_color = _eval_param_c(node, 'stroke_colorr', 'stroke_colorg', 'stroke_colorb', (1, 1, 1))
            stroke_projtype = _eval_param(node, 'stroke_projtype', 0)
            stroke_projcenter = _eval_param_v3(node, 'stroke_projcenterx', 'stroke_projcentery', 'stroke_projcenterz', (0, 0, 0))

            proj_dir = _projection_dir(stroke_projtype, self.mouse_dir)

            mirrorlist = self.activeMirrorTransforms(node)

            if stroke_numstrokes == 0 or not update:
                stroke_numstrokes += len(mirrorlist)

            stroke_numstrokes_param.set(stroke_numstrokes)

            activestroke = stroke_numstrokes - len(mirrorlist) + 1

            # users should use reset_active_stroke to reset it
            # this check might catch if self.strokes was set to empty
            if self.strokesNextToEncode > len(self.strokes):
                self.strokesNextToEncode = 0
                self.strokesMirrorData = []

            # check if cache array has enough size
            extraMirrors = len(mirrorlist) - len(self.strokesMirrorData)
            if extraMirrors > 0:
                self.strokesMirrorData.extend(
                    [su.ByteStream() for _ in range(extraMirrors)])

            for (mirror, mirrorData) in zip(mirrorlist, self.strokesMirrorData):
                meta_data_array = self.buildMetaDataArray(node, ui_event, captured_parms, mirror)
                stroke_meta_data = StrokeMetaData.create(node, meta_data_array)

                # update the stroke parameter set
                params = StrokeParams(node, activestroke, param_prefix)
                activestroke = activestroke + 1

                # ---
                # removed extra parms
                # ---
                # params.radius.set(5)
                # params.opacity.set(stroke_opacity)
                # params.tool.set(stroke_tool)
                # (r, g, b) = stroke_color.rgb()
                # params.colorr.set(r)
                # params.colorg.set(g)
                # params.colorb.set(b)
                # params.projtype.set(stroke_projtype)
                # params.projcenterx.set(stroke_projcenter[0])
                # params.projcentery.set(stroke_projcenter[1])
                # params.projcenterz.set(stroke_projcenter[2])
                # params.projdirx.set(proj_dir[0])
                # params.projdiry.set(proj_dir[1])
                # params.projdirz.set(proj_dir[2])

                mirroredstroke = StrokeData.create()
                for i in range(self.strokesNextToEncode, len(self.strokes)):
                    stroke = self.strokes[i]
                    mirroredstroke.reset()
                    mirroredstroke.pos = stroke.pos * mirror
                    dir4 = hou.Vector4(stroke.dir)
                    dir4[3] = 0
                    dir4 = dir4 * mirror
                    mirroredstroke.dir = hou.Vector3(dir4)

                    mirroredstroke.proj_pos = hou.Vector3(0.0, 0.0, 0.0)
                    mirroredstroke.proj_uv = hou.Vector3(0.0, 0.0, 0.0)
                    mirroredstroke.proj_prim = -1,
                    mirroredstroke.proj_success = False,
                    mirroredstroke.pressure = stroke.pressure
                    mirroredstroke.time = stroke.time
                    mirroredstroke.tilt = stroke.tilt
                    mirroredstroke.angle = stroke.angle
                    mirroredstroke.roll = stroke.roll

                    (mirroredstroke.proj_pos, _, mirroredstroke.proj_uv, mirroredstroke.proj_prim, mirroredstroke.proj_success) = self.cursor.project_point(node, mirroredstroke.pos, mirroredstroke.dir, self.intersectGeometry(node))

                    mirrorData.add(mirroredstroke.encode(), su.ByteStream)

                # store the stroke points
                params.data.set(self.bytes(mirrorData))
                try:
                    # NOTE: the node may not have a meta data parameter
                    params.metadata.set(stroke_meta_data)
                except AttributeError:
                    pass

            self.strokesNextToEncode = len(self.strokes)
            self.onPostApplyStroke(node, ui_event, captured_parms)

    @su.trace
    def stroke_from_event(self, ui_event, device, node):
        """ Create a stroke data struct from a UI device event and mouse
            point projection on the geometry

            Used internally.
        """
        sdata = StrokeData.create()
        (mouse_point, mouse_dir) = ui_event.screenToRay(device.mouseX(), device.mouseY())

        sdata.pos = mouse_point
        sdata.dir = mouse_dir
        sdata.pressure = device.tabletPressure()
        sdata.tile = device.tabletTilt()
        sdata.angle = device.tabletAngle()
        sdata.roll = device.tabletRoll()

        if device.time() >= 0:
            sdata.time = device.time() - self.epoch_time
        else:
            sdata.time = self.stopwatch.elapsed()

        (sdata.proj_pos, _, sdata.proj_uv, sdata.proj_prim, sdata.proj_success) = self.cursor.project_point(node, sdata.pos, sdata.dir, self.intersectGeometry(node))
        return sdata

    @su.trace
    def handle_stroke_event(self, ui_event, node):
        """ Registers stroke event(s) and deals with the queued
            devices if any

            Used internally.
        """
        first_device = ui_event.device()
        if ui_event.hasQueuedEvents() is True:
            first_device = ui_event.queuedEvents()[0]

        if len(self.strokes) == 0:
            if first_device.time() >= 0:
                self.epoch_time = first_device.time()
            else:
                self.stopwatch.start()

        for qevent in ui_event.queuedEvents():
            sd = self.stroke_from_event(ui_event, qevent, node)
            self.strokes.append(sd)

        sd = self.stroke_from_event(ui_event, ui_event.device(), node)

        if ui_event.reason() == hou.uiEventReason.Changed and self.strokes:
            sd.pressure = self.strokes[-1].pressure
            sd.tilt = self.strokes[-1].tilt
            sd.angle = self.strokes[-1].angle
            sd.roll = self.strokes[-1].roll

        self.strokes.append(sd)

def createStrokeStateTemplate(state_typename, state_label, icon_name, state_class_type,
    extend_template_func=None):
    """
    Create and configure a new stroke viewer state. 
    Derived class should call this function to register their own 
    state and re-use the stroke bindings.
    
    state_typename: State type name
    state_label: State label name
    icon_name: State icon name or file path
    state_class_type: State implementation class type
    extend_template_func: Optional function for extending the new template with bindings.
                          Arguments:
                            template: hou.ViewerStateTemplate object to use for 
                                      binding new items.
                            menu:     Top level hou.ViewerStateMenu object for adding
                                      new menu items. 
    """
    state_cat = hou.sopNodeTypeCategory()
    t = hou.ViewerStateTemplate(state_typename, state_label, state_cat)

    t.bindFactory(state_class_type)    
    t.bindIcon(icon_name)

    # hotkeys
    hotkey_definitions = hou.PluginHotkeyDefinitions()

    realtime = su.defineHotkey(hotkey_definitions,
        state_typename, 'realtime_mode', '0', 'realtime', 'Enable realtime mode')
    cycle_brushes = su.defineHotkey(hotkey_definitions,
        state_typename, 'cycle_brushes', '1', 'Cycle brushes', 'Cycle stroke tools')
    set_wireframe_brush = su.defineHotkey(hotkey_definitions,
        state_typename, 'set_wireframe_brush', '2', 'Set wireframe brush')
    set_viewport_brush = su.defineHotkey(hotkey_definitions,
        state_typename, 'set_viewport_brush', '3', 'Set viewport brush')

    t.bindHotkeyDefinitions(hotkey_definitions)

    # define the popup menu
    m = hou.ViewerStateMenu('stroke_menu', 'Stroke')

    m.addToggleItem('realtime_mode', 'Draw realtime', True, hotkey=realtime)
    m.addSeparator()

    # add brush menu
    brush_menu = hou.ViewerStateMenu('brush_menu', 'Brush settings...')
    brush_menu.addActionItem('cycle_brushes', 'Cycle brushes', hotkey=cycle_brushes)
    brush_menu.addRadioStrip('brush_display_mode', 'Brush display mode', 'brush_viewport_display')
    brush_menu.addRadioStripItem('brush_display_mode', 'brush_wireframe_display', 'Wireframe', hotkey=set_wireframe_brush)
    brush_menu.addRadioStripItem('brush_display_mode', 'brush_viewport_display', 'Viewport', hotkey=set_viewport_brush)
    brush_menu.addSeparator()
    m.addMenu(brush_menu)
    m.addSeparator()

    # extend the template
    if extend_template_func:
        extend_template_func(t, m)
    
    # bind the popup menu to the stroke state
    t.bindMenu(m)

    return t
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# interface with houdini

def createViewerStateTemplate():
    """
    Create and configure a new stroke viewer state
    """
    state_typename = 'sidefx_stroke'
    state_label = 'Stroke'
    icon_name = '$HFS/houdini/pic/minimizedicon.pic'
    
    return createStrokeStateTemplate(state_typename, state_label, icon_name, StrokeState)


