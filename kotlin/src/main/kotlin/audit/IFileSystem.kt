package audit

interface IFileSystem {

    fun getFiles(directoryName: String): List<String>

    fun writeAllText(filePath: String, content: String)

    fun readAllLines(filePath: String): MutableList<String>
}
