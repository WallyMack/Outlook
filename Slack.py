import requests
from setting import Slack_Team, Slack_Token, Slack_Channel
import time

def slack_message(message, channel):
	slackToken = Slack_Token
	slackTeam = Slack_Team
	requests.post("https://"+ slackTeam + "/services/hooks/slackbot?token=" +
					  slackToken + "&channel=%23" + channel, data = message)

def slack_alert(Exc,icon,status):
	# print('Auto Product Order Fail, Alert Slack')
	# exception =
	message = """
========================================
%s PROBLEM: Problem name: 注意
%s。 
Problem happened at %s on %s
告警事件
訂單失敗類別 : %s
========================================
	""" % (icon,status, time.strftime("%H:%M:%S", time.localtime()), time.strftime("%Y.%m.%d", time.localtime()), Exc)
	message = message.encode('utf-8')
	slack_message(message, Slack_Channel)
	print(message)

if __name__ == "__main__":
	slack_message(':sob: Auto Product Order Fail' \
				  'Please Check Product Order Flow','bigdata')
