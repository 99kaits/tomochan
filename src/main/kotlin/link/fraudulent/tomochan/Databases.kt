package link.fraudulent.tomochan

import io.ktor.server.application.*
import java.sql.Connection
import java.sql.DriverManager

fun Application.configureDatabases() {
    val dbConnection: Connection = connectToDB(environment.config.property("postgres.embedded").getString().toBoolean())
    val closed = dbConnection.isClosed
    print("Is Db closed?: $closed")
}

fun Application.connectToDB(embedded: Boolean): Connection {
    Class.forName("org.postgresql.Driver")
    if (embedded) { //Use the Embedded DB H2
        log.info("Connecting to embedded db; use only for testing")
        return DriverManager.getConnection("jdbc:h2:mem:test;DB_CLOSE_DELAY=-1", "root", "")
    } else {
        val url = environment.config.property("postgres.url").getString() //Get URL from application.yaml
        log.info("Connecting to db at $url")
        val user = environment.config.property("postgres.user").getString() //Get from application.yaml
        val password = environment.config.property("postgres.user").getString() //Get from application.yaml

        return DriverManager.getConnection(url, user, password)
    }
}