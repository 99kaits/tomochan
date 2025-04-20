package link.fraudulent.tomochan

import io.ktor.server.application.*
import io.ktor.server.plugins.requestvalidation.*

fun main(args: Array<String>) {
    io.ktor.server.jetty.jakarta.EngineMain.main(args)
}

fun Application.module() {
    configureDatabases()
}