package link.fraudulent.tomochan

import kotlinx.coroutines.*
import kotlinx.serialization.*
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object LocalDateTimeSerializer : KSerializer<LocalDateTime> {
    private val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

    override val descriptor: SerialDescriptor =
        PrimitiveSerialDescriptor("LocalDateTime", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: LocalDateTime) {
        encoder.encodeString(value.format(formatter))
    }

    override fun deserialize(decoder: Decoder): LocalDateTime {
        return LocalDateTime.parse(decoder.decodeString(), formatter)
    }
}

@Serializable
data class Board(
    val threadId: Long? = null, // Maps the foreign key reference
    @Serializable(with = LocalDateTimeSerializer::class)
    val lastBump: LocalDateTime? = null,
    val sticky: Boolean? = null,
    @Serializable(with = LocalDateTimeSerializer::class)
    val time: LocalDateTime,
    val poster: String,
    val email: String? = null,
    val subject: String? = null,
    val content: String,
    val filename: String? = null,
    val password: String? = null,
    val spoiler: Boolean,
    val ip: String
)
class BoardService(private val connection: Connection) {
    companion object {
        private const val CREATE_SEQUENCE = "CREATE SEQUENCE IF NOT EXISTS shared_id_seq START 1 INCREMENT 1 NO MINVALUE NO MAXVALUE CACHE 1;"
        private const val CREATE_PARENT = """
            CREATE TABLE IF NOT EXISTS parent_board (
                id BIGINT DEFAULT nextval('shared_id_seq') PRIMARY KEY,
                thread_id BIGINT REFERENCES parent_board(id),
                last_bump TIMESTAMP,
                sticky BOOLEAN,
                time TIMESTAMP NOT NULL,
                poster TEXT NOT NULL,
                email VARCHAR(255),
                subject TEXT,
                content TEXT NOT NULL,
                filename TEXT,
                password TEXT,
                spoiler BOOLEAN NOT NULL,
                ip VARCHAR(45)  NOT NULL
            );
            """

        // CREATE_BOARD with dynamic table name (constructed at runtime)
        fun createBoardSql(tableName: String): String {
            validateTableName(tableName)
            return "CREATE TABLE IF NOT EXISTS $tableName () INHERITS (parent_board);"
        }

        // INSERT_POST with dynamic table name (constructed at runtime)
        fun insertPostSql(tableName: String): String {
            validateTableName(tableName)
            return """
            INSERT INTO $tableName (
              thread_id, 
              last_bump, 
              sticky, 
              time, 
              poster, 
              email, 
              subject, 
              content, 
              filename, 
              password, 
              spoiler, 
              ip
            ) VALUES (
              ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            );
        """.trimIndent()
        }

        // DELETE_POST with dynamic table name (constructed at runtime)
        fun deletePostSql(tableName: String): String {
            validateTableName(tableName)
            return "DELETE FROM $tableName WHERE id = ?;"
        }

        fun selectPostSql(tableName: String): String {
            validateTableName(tableName)
            return "SELECT FROM $tableName WHERE id = ?;"
        }

        // Validate table name
        private fun validateTableName(tableName: String) {
            val regex = Regex("^[a-zA-Z_][a-zA-Z0-9_]*$")
            require(tableName.matches(regex)) { "Invalid table name: $tableName" }
        }
    }

    init {
        //TODO: Improve this later
        connection.createStatement().use {
            it.executeUpdate(CREATE_SEQUENCE)
            it.executeUpdate(CREATE_PARENT)
            it.executeUpdate(createBoardSql("b"))
        }
    }

    suspend fun test(): String = withContext(Dispatchers.IO) {
            return@withContext "test"
    }

    suspend fun read(board: String, id: Int): Board = withContext(Dispatchers.IO) {
        val statement = connection.prepareStatement(selectPostSql(board))
        statement.setInt(1, id)
        val resultSet = statement.executeQuery()
        if (resultSet.next()) {
            val threadId = resultSet.getLong("threadID")
            val laspBump = LocalDateTime.parse(resultSet.getString("lastBump"), DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
            val sticky = resultSet.getBoolean("sticky")
            val time = LocalDateTime.parse(resultSet.getString("time"), DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
            val poster = resultSet.getString("poster")
            val email = resultSet.getString("email")
            val subject = resultSet.getString("subject")
            val content = resultSet.getString("content")
            val filename = resultSet.getString("filename")
            val password= resultSet.getString("password")
            val spoiler = resultSet.getBoolean("spoiler")
            val ip = resultSet.getString("ip")
            return@withContext Board(threadId,laspBump, sticky, time, poster, email, subject, content, filename, password, spoiler, ip)
        }
        throw Exception("Yo wtf can't read that, stop making stuff up bro like wtf.")
    }
}
