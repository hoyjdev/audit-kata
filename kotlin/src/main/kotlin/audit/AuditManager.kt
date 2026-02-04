package audit

import java.nio.file.Paths
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

class AuditManager(
    private val maxEntriesPerFile: Int,
    private val directoryName: String,
    private val fileSystem: IFileSystem
) {

    fun addRecord(visitorName: String, timeOfVisit: LocalDateTime) {
        val filePaths = fileSystem.getFiles(directoryName)
        val sorted = sortByIndex(filePaths)
        val dateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        val newRecord = "$visitorName;${timeOfVisit.format(dateTimeFormatter)}"

        if (sorted.isEmpty()) {
            val newFile = Paths.get(directoryName, "audit_1.txt").toString()
            fileSystem.writeAllText(newFile, newRecord)
            return
        }

        val currentFileIndex = sorted.size - 1
        val currentFilePath = sorted[currentFileIndex]
        val lines = fileSystem.readAllLines(currentFilePath)

        if (lines.size < maxEntriesPerFile) {
            lines += newRecord
            val newContent = lines.joinToString(separator = System.lineSeparator())
            fileSystem.writeAllText(currentFilePath, newContent)
        } else {
            val newName = "audit_${currentFileIndex + 2}.txt"
            val newFile: String = Paths.get(directoryName, newName).toString()
            fileSystem.writeAllText(newFile, newRecord)
        }
    }

    private fun sortByIndex(filePaths: List<String>): List<String> {
        return filePaths.sorted()
    }
}
