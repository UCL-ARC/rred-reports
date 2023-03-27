import asyncio
import smtpd


class MockSMTPServer(smtpd.SMTPServer):
    def __init__(*args, **kwargs):
        smtpd.SMTPServer.__init__(*args, **kwargs)

    def process_message(*args, **kwargs):
        pass


if __name__ == "__main__":
    smtp_server = MockSMTPServer(("localhost", 9000), None)
    try:
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except KeyboardInterrupt:
        smtp_server.close()
