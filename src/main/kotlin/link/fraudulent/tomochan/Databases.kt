package link.fraudulent.tomochan

import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import java.sql.Connection
import java.sql.DriverManager

fun Application.configureDatabases() {
    val dbConnection: Connection = connectToDB()
    val boardService = BoardService(dbConnection)


    routing {
        get("/{board}/{id}") {
            val board = call.parameters["board"] ?: throw IllegalArgumentException("Invalid board")
            val id = call.parameters["id"]?.toLong() ?: throw IllegalArgumentException("Invalid ID")
            try {
                val post = boardService.read(board,id)
                val thread = boardService.threadIds(id)
                call.respond(HttpStatusCode.OK, post.toString() + thread.toString())
            } catch (e: Exception) {
                call.respond(HttpStatusCode.NotFound, message = e.toString())
            }
        }
        get("/{board}") {
            val board = call.parameters["board"] ?: throw IllegalArgumentException("Invalid board")
            try {
                val ids = boardService.ids(board)
                val postList = ids.map { id -> boardService.read(board, id) }
                call.respond(HttpStatusCode.OK, postList.toString())
            } catch (e: Exception) {
                call.respond(HttpStatusCode.NotFound, message = e.toString())
            }
        }
    }
}

fun Application.connectToDB(): Connection {
    Class.forName("org.postgresql.Driver")
        val url = environment.config.property("postgres.url").getString() //Get URL from application.yaml
        log.info("Connecting to db at $url")
        val user = environment.config.property("postgres.user").getString() //Get from application.yaml
        val password = environment.config.property("postgres.password").getString() //Get from application.yaml

        return DriverManager.getConnection(url, user, password)
}