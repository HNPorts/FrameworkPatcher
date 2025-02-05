import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def prepatch(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    if not any('invoke-custom' in line for line in lines):
        logging.info(f"No invoke-custom found in file: {filepath}. Skipping modification.")
        return

    modified_lines = []
    in_method = False
    method_type = None
    method_patterns = {
        "equals": re.compile(r'\.method.*equals\(Ljava/lang/Object;\)Z'),
        "hashCode": re.compile(r'\.method.*hashCode\(\)I'),
        "toString": re.compile(r'\.method.*toString\(\)Ljava/lang/String;')
    }
    registers_line = ""

    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                registers_line = line
                continue

            if line.strip() == '.end method':
                if method_type in method_patterns:
                    logging.info(f"Clearing method body for {method_type}")
                    modified_lines.append(registers_line)
                    if method_type == "hashCode":
                        modified_lines.append("    const/4 v0, 0x0\n")
                        modified_lines.append("    return v0\n")
                    elif method_type == "equals":
                        modified_lines.append("    const/4 v0, 0x0\n")
                        modified_lines.append("    return v0\n")
                    elif method_type == "toString":
                        modified_lines.append("    const/4 v0, 0x0\n")
                        modified_lines.append("    return-object v0\n")
                in_method = False
                method_type = None
                registers_line = ""
            else:
                continue

        for key, pattern in method_patterns.items():
            if pattern.search(line):
                logging.info(f"Found method {key}. Clearing method content.")
                in_method = True
                method_type = key
                modified_lines.append(line)  # Add method declaration to output
                break

        if not in_method:
            modified_lines.append(line)

    with open(filepath, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Completed modification for file: {filepath}")

def modify_file(file_path, search_pattern, add_line_template):
    logging.info(f"Modifying file: {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        modified_lines.append(line)
        match = re.search(search_pattern, line)
        if match:
            vX = match.group(1)
            add_line = add_line_template.format(vX=vX)
            logging.info(f"Found pattern in file: {file_path} with variable {vX}")
            modified_lines.append(add_line + '\n')

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Completed modification for file: {file_path}")


def modify_not_allow_capture_display(file_path):
    logging.info(f"Modifying notAllowCaptureDisplay method in file: {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    in_method = False
    method_start_line = ""
    search_pattern = re.compile(
        r'\.method public notAllowCaptureDisplay\(Lcom/android/server/wm/RootWindowContainer;I\)Z')

    for line in lines:
        if in_method:
            if line.strip() == '.end method':
                # Add method body
                modified_lines.append(method_start_line)
                modified_lines.append("    .registers 9\n")
                modified_lines.append("    const/4 v0, 0x0\n")
                modified_lines.append("    return v0\n")
                in_method = False
                method_start_line = ""
            else:
                continue

        if search_pattern.search(line):
            in_method = True
            method_start_line = line
        else:
            modified_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Completed modification for notAllowCaptureDisplay method in file: {file_path}")


def modify_smali_files(directories):
    classes_to_modify = [
        'com/android/server/AppOpsServiceStubImpl.smali',
        'com/android/server/alarm/AlarmManagerServiceStubImpl.smali',
        'com/android/server/am/BroadcastQueueModernStubImpl.smali',
        'com/android/server/am/ProcessManagerService.smali',
        'com/android/server/am/ProcessSceneCleaner.smali',
        'com/android/server/job/JobServiceContextImpl.smali',
        'com/android/server/notification/NotificationManagerServiceImpl.smali',
        'com/miui/server/greeze/GreezeManagerService.smali',
        'miui/app/ActivitySecurityHelper.smali',
        'com/android/server/am/ActivityManagerServiceImpl.smali',
        'com/android/server/ForceDarkAppListManager.smali',
        'com/android/server/am/ActivityManagerServiceImpl$1.smali',
        'com/android/server/input/InputManagerServiceStubImpl.smali',
        'com/android/server/inputmethod/InputMethodManagerServiceImpl.smali',
        'com/android/server/wm/MiuiSplitInputMethodImpl.smali',
        'com/android/server/wm/WindowManagerServiceImpl.smali'
    ]

    search_pattern = r'sget-boolean (v\d+), Lmiui/os/Build;->IS_INTERNATIONAL_BUILD:Z'
    add_line_template = '    const/4 {vX}, 0x1'

    for directory in directories:
        pre_patch1 = os.path.join(directory, 'com/android/server/input/InputDfsReportStubImpl$MessageObject.smali')
        pre_patch2 = os.path.join(directory, 'com/android/server/input/InputOneTrackUtil$TrackEventListData.smali')
        pre_patch3 = os.path.join(directory, 'com/android/server/input/InputOneTrackUtil$TrackEventStringData.smali')
        pre_patch4 = os.path.join(directory, 'com/android/server/policy/MiuiScreenOnProximityLock$AcquireMessageObject.smali')
        pre_patch5 = os.path.join(directory, 'com/android/server/policy/MiuiScreenOnProximityLock$ReleaseMessageObject.smali')

        if os.path.exists(pre_patch1):
            prepatch(pre_patch1)
        if os.path.exists(pre_patch2):
            prepatch(pre_patch2)
        if os.path.exists(pre_patch3):
            prepatch(pre_patch3)
        if os.path.exists(pre_patch4):
            prepatch(pre_patch4)
        if os.path.exists(pre_patch5):
            prepatch(pre_patch5)
        for class_file in classes_to_modify:
            file_path = os.path.join(directory, class_file)
            if os.path.exists(file_path):
                logging.info(f"Found file: {file_path}")
                modify_file(file_path, search_pattern, add_line_template)
                if class_file == 'com/android/server/wm/WindowManagerServiceImpl.smali':
                    modify_not_allow_capture_display(file_path)
            else:
                logging.warning(f"File not found: {file_path}")


if __name__ == "__main__":
    directories = ["miui_services_classes"]
    modify_smali_files(directories)
