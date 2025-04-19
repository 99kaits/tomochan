plugins {
    alias(libs.plugins.kotlin.jvm)
}

group = "link.fraudulent"
version = "0.0.1"

repositories {
    mavenCentral()
    maven { url = uri("https://packages.confluent.io/maven/") }
}

dependencies {
    implementation(libs.logback.classic)
}