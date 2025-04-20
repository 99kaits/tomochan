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


    val closed = dbConnection.isClosed
    print("Is Db closed?: $closed")

    routing {
        get("/test") {
            val test = boardService.test()
            call.respond(HttpStatusCode.OK, test)
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