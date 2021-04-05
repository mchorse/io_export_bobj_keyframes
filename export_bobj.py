import os

import bpy

from progress_report import ProgressReport, ProgressReportSubstep

# Remove spaces from given string (so it would be spaceless)
def name_compat(name):
    return 'None' if name is None else name.replace(' ', '_')

# Writes all action keyframes
def write_actions(context, fw):
    fw('# Animation data\n')
    
    # Exporting animation actions
    for key, action in bpy.data.actions.items():
        write_action(context, fw, key, action)
                   
# Write an action
def write_action(context, fw, name, action):
    groups = {}
    
    def getOrCreate(key):
        if key in groups:
            return groups[key]
        
        l = []
        groups[key] = l
        
        return l
    
    # Collect groups
    for fc in action.fcurves:
        if fc.data_path.startswith('pose.bones["'):
            key = fc.data_path[12:]
            key = key[:key.index('"')]
            
            getOrCreate(key).append(fc)
    
    # Don't write anything if this action is empty
    if not groups:
        return
    
    fw('an %s\n' % name)
    
    for key, group in groups.items():
        fw('ao %s\n' % name_compat(key))
        
        for fcurve in group:
            data_path = fcurve.data_path
            index = fcurve.array_index
            length = len(fcurve.keyframe_points)
            dvalue = 0
        
            if data_path.endswith('location'):
                data_path = 'location'
            elif data_path.endswith('rotation_euler'):
                data_path = 'rotation'
            elif data_path.endswith('scale'):
                data_path = 'scale'
                dvalue = 1
            else:
                continue
            
            if length <= 0:
                continue

            all_default = True

            # Prevent writing actions which fully consist out of default values
            for keyframe in fcurve.keyframe_points:
                if keyframe.co[1] != dvalue:
                    all_default = False

                    break;

            if all_default: 
                continue

            # Write the action group
            fw('ag %s %d\n' % (data_path, index))
        
            last_frame = None
        
            for keyframe in fcurve.keyframe_points:
                # Avoid inserting keyframes with duplicate X value
                if last_frame == keyframe.co[0]:
                    continue
            
                fw(stringify_keyframe(context, keyframe) + '\n')
                last_frame = keyframe.co[0]

# Stringify a keyframe
def stringify_keyframe(context, keyframe):
    fps = context.scene.render.fps
    f = 20 / fps

    interp = keyframe.interpolation
    result = 'kf %f %f %s' % (float(keyframe.co[0]) * float(f), keyframe.co[1], interp)
    result += ' %f %f %f %f' % (keyframe.handle_left[0] * f, keyframe.handle_left[1], keyframe.handle_right[0] * f, keyframe.handle_right[1])
    
    return result

def save(context, filepath):
    with ProgressReport(context.window_manager) as progress:
        scene = context.scene

        progress.enter_substeps(1)
        write_file(context, filepath, scene, progress)
        progress.leave_substeps()

    return {'FINISHED'}

def write_file(context, filepath, scene, progress=ProgressReport()):
    with ProgressReportSubstep(progress, 2, "BOBJ Export path: %r" % filepath, "BOBJ Export Finished") as subprogress1:
        with open(filepath, "w", encoding="utf8", newline="\n") as f:
            fw = f.write

            # Write Header
            fw('# Blender v%s BOBJ keyframes: %r\n' % (bpy.app.version_string, os.path.basename(bpy.data.filepath)))

            # Write keyframes to the file   
            write_actions(context, fw)
            
        subprogress1.step("Finished exporting keyframes")