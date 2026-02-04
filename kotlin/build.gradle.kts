plugins {
    kotlin("jvm") version "2.3.0"
}

group = "audit"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:1.14.9")
}

kotlin {
    jvmToolchain(25)
}

tasks.test {
    useJUnitPlatform()
}