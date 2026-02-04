package audit;

import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.List;

public class AuditManager {

    private final int maxEntriesPerFile;
    private final String directoryName;
    private final IFileSystem fileSystem;
    private final DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public AuditManager(int maxEntriesPerFile, String directoryName, IFileSystem fileSystem) {
        this.maxEntriesPerFile = maxEntriesPerFile;
        this.directoryName = directoryName;
        this.fileSystem = fileSystem;
    }

    // nu 2 responsibilities: I/O en audits verwerken
    public void addRecord(String visitorName, LocalDateTime timeOfVisit) {
        String newRecord = createRecordFrom(visitorName, timeOfVisit);

        String[] currentFiles = getCurrentFilesSortedByName();
        if (currentFiles.length == 0) {
            writeNewRecordToNewFile(newRecord);
            return;
        }

        int currentFileIndex = currentFiles.length - 1;
        String currentFilePath = currentFiles[currentFileIndex];
        List<String> lines = fileSystem.readAllLines(currentFilePath);

        if (lines.size() < maxEntriesPerFile) {
            lines.add(newRecord);
            String newContent = String.join(System.lineSeparator(), lines);
            fileSystem.writeAllText(currentFilePath, newContent);
        } else {
            String newFile = createNewAuditFile(currentFileIndex);
            fileSystem.writeAllText(newFile, newRecord);
        }
    }

    private void writeNewRecordToNewFile(String newRecord) {
        String newFile = Paths.get(directoryName, "audit_1.txt").toString();
        fileSystem.writeAllText(newFile, newRecord);
    }

    private String[] getCurrentFilesSortedByName() {
        String[] filePaths = fileSystem.getFiles(directoryName);
        String[] sorted = sortByIndex(filePaths);
        return sorted;
    }

    private String createRecordFrom(String visitorName, LocalDateTime timeOfVisit) {
        return visitorName + ";" + timeOfVisit.format(dateTimeFormatter);
    }

    private String createNewAuditFile(int currentFileIndex) {
        String newName = "audit_" + (currentFileIndex + 2) + ".txt";
        return Paths.get(directoryName, newName).toString();
    }

    private String[] sortByIndex(String[] filePaths) {
        return Arrays.stream(filePaths)
                .sorted()
                .toArray(String[]::new);
    }
}
