import smtplib
import time
import os
import sys
import threading
import json
from queue import Queue
import ctypes
import random

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

sent_email_count = 0

def update_title():
    ctypes.windll.kernel32.SetConsoleTitleW(f"Email Spammer | Sent: {sent_email_count}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    clear_screen()

def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

def get_user_input():
    config = load_config()
    
    mode = config["mode"]
    recipient_email = input(bcolors.OKGREEN + 'To: ' + bcolors.ENDC)
    subject = input(bcolors.OKGREEN + 'Subject (Optional): ' + bcolors.ENDC)
    message_body = input(bcolors.OKGREEN + 'Message: ' + bcolors.ENDC)
    total_emails = int(input(bcolors.OKGREEN + 'Total Number of Emails to send: ' + bcolors.ENDC))

    message = f'Subject: {subject}\n\n{message_body}'

    return mode, recipient_email, message, total_emails

def send_emails(server_choice, user, pwd, to, message, num_emails):
    global sent_email_count
    try:
        if server_choice == '1':
            server = smtplib.SMTP("smtp.gmail.com", 587)
        elif server_choice == '2':
            server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
        elif server_choice == '3':
            server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        else:
            return

        server.starttls()
        server.login(user, pwd)
        
        for _ in range(num_emails):
            try:
                server.sendmail(user, to, message)
                sent_email_count += 1
                update_title()
                print(bcolors.OKGREEN + f'[Success] Sent Email | {user}' + bcolors.ENDC)
                time.sleep(.8)
            except KeyboardInterrupt:
                print(bcolors.FAIL + '\nCanceled' + bcolors.ENDC)
                sys.exit()
            except smtplib.SMTPAuthenticationError:
                print('\nThe username or password you entered is incorrect.')
                sys.exit()
            except Exception as e:
                print(bcolors.FAIL +f"[Failed] Failed to send email | {user}")

        server.quit()

    except smtplib.SMTPAuthenticationError:
        print(bcolors.FAIL + 'Authentication failed. Check your credentials and try again.' + bcolors.ENDC)
    except Exception as e:
        print(f"An error occurred: {e}")

def thread_worker(queue, server_choice, recipient_email, message):
    while not queue.empty():
        user, password = queue.get()
        send_emails(server_choice, user, password, recipient_email, message, 1)
        queue.task_done()

def main():
    display_banner()

    config = load_config()
    try:
        mode, recipient_email, message, total_emails = get_user_input()
        num_threads = config["threads"]

        if mode == "Single":
            user_email = config["user_email"]
            password = config["password"]
            server_choice = config["server_choice"]

            queue = Queue()
            for _ in range(total_emails):
                queue.put((user_email, password))

            threads = []
            for _ in range(num_threads):
                thread = threading.Thread(target=thread_worker, args=(queue, server_choice, recipient_email, message))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        elif mode == "Multi":
            with open(config["accs_file"], "r") as accs_file:
                accounts = [line.strip().split(":") for line in accs_file.readlines()]
            
            random.shuffle(accounts)
            
            server_choice = config["server_choice"]
            num_threads = config["threads"]

            queue = Queue()
            for account in accounts:
                queue.put(account)

            threads = []
            for _ in range(num_threads):
                thread = threading.Thread(target=thread_worker, args=(queue, server_choice, recipient_email, message))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

    except KeyboardInterrupt:
        print(bcolors.FAIL + '\nCanceled by user' + bcolors.ENDC)
        sys.exit()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
