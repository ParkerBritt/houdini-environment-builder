import hou

def state_from_node(hda_node, node_path):
    node = hda_node.node(node_path)
    node.setCurrent(True, True)
    scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer , index=0)
    scene_viewer.pane().setIsMaximized(True)
    scene_viewer.enterCurrentNodeState(wait_for_exit=True)
    print('exited')
    hda_node.setCurrent(True, True)
    scene_viewer.pane().setIsMaximized(False)
