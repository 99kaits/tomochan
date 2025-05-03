package link.fraudulent.tomochan

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder
import java.sql.Connection
import java.sql.SQLException
import java.sql.Timestamp
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object LocalDateTimeSerializer : KSerializer<LocalDateTime> {
    private val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss[.S]")

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
    val sticky: Boolean,
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
                sticky BOOLEAN NOT NULL,
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
        private const val GET_THREAD_IDS = "SELECT id FROM parent_board WHERE thread_id = ?"

        // CREATE_BOARD with dynamic table name (constructed at runtime)
        private fun createBoardSql(tableName: String): String {
            validateTableName(tableName)
            return "CREATE TABLE IF NOT EXISTS $tableName () INHERITS (parent_board);"
        }

        // INSERT_POST with dynamic table name (constructed at runtime)
        private fun insertPostSql(tableName: String): String {
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
        private fun deletePostSql(tableName: String): String {
            validateTableName(tableName)
            return "DELETE FROM $tableName WHERE id = ?;"
        }

        private fun selectPostSql(tableName: String): String {
            validateTableName(tableName)
            return """
        SELECT
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
        FROM $tableName
        WHERE id = ?;
        """.trimIndent()
        }

        fun getId(tablename: String): String {
            validateTableName(tablename)
            return "SELECT id FROM $tablename"
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

    suspend fun read(table: String, id: Long): Board = withContext(Dispatchers.IO) {
        val statement = connection.prepareStatement(selectPostSql(table))
        statement.setLong(1, id)
        val resultSet = statement.executeQuery()
        if (resultSet.next()) {
            val threadId = resultSet.getLong("thread_id")
            val lastBump = resultSet.getTimestamp("last_bump")?.toLocalDateTime()
            val sticky = resultSet.getBoolean("sticky")
            val time = resultSet.getTimestamp("time").toLocalDateTime()
            val poster = resultSet.getString("poster")
            val email = resultSet.getString("email")
            val subject = resultSet.getString("subject")
            val content = resultSet.getString("content")
            val filename = resultSet.getString("filename")
            val password= resultSet.getString("password")
            val spoiler = resultSet.getBoolean("spoiler")
            val ip = resultSet.getString("ip")
            return@withContext Board(threadId,lastBump, sticky, time, poster, email, subject, content, filename, password, spoiler, ip)
        }
        throw Exception("Yo wtf can't read that, stop making stuff up bro like wtf.")
    }

    suspend fun create(table: String, board: Board): Int = withContext(Dispatchers.IO) {
        val statement = connection.prepareStatement(insertPostSql(table))
        board.threadId?.let {
            statement.setLong(1, it)
        } ?: statement.setNull(1, java.sql.Types.BIGINT)
        board.lastBump?.let {
            statement.setTimestamp(2, Timestamp.valueOf(it))
        } ?: statement.setNull(2, java.sql.Types.TIMESTAMP)
        statement.setBoolean(3,board.sticky)
        board.time?.let {
            statement.setTimestamp(4, Timestamp.valueOf(it))
        } ?: statement.setNull(4, java.sql.Types.TIMESTAMP)
        statement.setString(5,board.poster)
        statement.setString(6,board.email)
        statement.setString(7,board.subject)
        statement.setString(8,board.content)
        statement.setString(9,board.filename)
        statement.setString(10,board.password)
        statement.setBoolean(11,board.spoiler)
        statement.setString(12,board.ip)
        statement.executeUpdate()
    }

    suspend fun delete(table: String, id: Int): Int = withContext(Dispatchers.IO) {
        val statement = connection.prepareStatement(deletePostSql(table))
        statement.setInt(1, id)
        statement.executeUpdate()
    }

    suspend fun ids(table: String): List<Long> = withContext(Dispatchers.IO) {
        return@withContext try {
            connection.prepareStatement(getId(table)).use { statement ->
                statement.executeQuery().use { resultSet ->
                    generateSequence {
                        if (resultSet.next()) resultSet.getLong("id") else null
                    }.toList()
                }
            }
        } catch (e: SQLException) {
            // Log the error and rethrow or return an empty list
            emptyList<Long>()
        }
    }

    suspend fun threadIds(id: Long): List<Long> = withContext(Dispatchers.IO) {
        try {
            connection.prepareStatement(GET_THREAD_IDS).use { statement ->
                statement.setLong(1,id)
                    statement.executeQuery().use { resultSet ->
                        return@withContext generateSequence {
                            if (resultSet.next()) resultSet.getLong("id") else null
                        }.toList()
                    }
                }
        } catch (e: SQLException) {
            // Log the error and rethrow or return an empty list (Depends on how we end up using this function)
            emptyList<Long>()
        }
    }
}
