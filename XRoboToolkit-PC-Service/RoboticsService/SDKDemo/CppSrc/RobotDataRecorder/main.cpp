//Main entry point for the Robot Data Recorder application
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include "SDKCaller.h"

#include "SensorDataHandler.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine;
    const QUrl url(u"qrc:/main.qml"_qs);
    qDebug() << "robot data recorder ..." <<Qt::endl;
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);
    qmlRegisterType<SDKCaller>("pico.qmlcomponents", 1, 0, "SDKCaller");

    return app.exec();
}
