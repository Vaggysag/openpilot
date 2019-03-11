from selfdrive.kegman_conf import kegman_conf

letters = { "a":[ "###", "# #", "###", "# #", "# #"], "b":[ "###", "# #", "###", "# #", "###"], "c":[ "###", "#", "#", "#", "###"], "d":[ "##", "# #", "# #", "# #", "##"], "e":[ "###", "#", "###", "#", "###"], "f":[ "###", "#", "###", "#", "#"], "g":[ "###", "# #", "###", "  #", "###"], "h":[ "# #", "# #", "###", "# #", "# #"], "i":[ "###", " #", " #", " #", "###"], "j":[ "###", " #", " #", " #", "##"], "k":[ "# #", "##", "#", "##", "# #"], "l":[ "#", "#", "#", "#", "###"], "m":[ "# #", "###", "###", "# #", "# #"], "n":[ "###", "# #", "# #", "# #", "# #"], "o":[ "###", "# #", "# #", "# #", "###"], "p":[ "###", "# #", "###", "#", "#"], "q":[ "###", "# #", "###", "  #", "  #"], "r":[ "###", "# #", "##", "# #", "# #"], "s":[ "###", "#", "###", "  #", "###"], "t":[ "###", " #", " #", " #", " #"], "u":[ "# #", "# #", "# #", "# #", "###"], "v":[ "# #", "# #", "# #", "# #", " #"], "w":[ "# #", "# #", "# #", "###", "###"], "x":[ "# #", " #", " #", " #", "# #"], "y":[ "# #", "# #", "###", "  #", "###"], "z":[ "###", "  #", " #", "#", "###"], " ":[ " "], "1":[ " #", "##", " #", " #", "###"], "2":[ "###", "  #", "###", "#", "###"], "3":[ "###", "  #", "###", "  #", "###"], "4":[ "#", "#", "# #", "###", "  #"], "5":[ "###", "#", "###", "  #", "###"], "6":[ "###", "#", "###", "# #", "###"], "7":[ "###", "  # ", " #", " #", "#"], "8":[ "###", "# #", "###", "# #", "###"], "9":[ "###", "# #", "###", "  #", "###"], "0":[ "###", "# #", "# #", "# #", "###"], "!":[ " # ", " # ", " # ", "   ", " # "], "?":[ "###", "  #", " ##", "   ", " # "], ".":[ "   ", "   ", "   ", "   ", " # "], "]":[ "   ", "   ", "   ", "  #", " # "], "/":[ "  #", "  #", " # ", "# ", "# "], ":":[ "   ", " # ", "   ", " # ", "   "], "@":[ "###", "# #", "## ", "#  ", "###"], "'":[ " # ", " # ", "   ", "   ", "   "], "#":[ " # ", "###", " # ", "###", " # "], "-":[ "  ", "  ","###","   ","   "] }
# letters stolen from here: http://www.stuffaboutcode.com/2013/08/raspberry-pi-minecraft-twitter.html

def print_letters(text):
    bigletters = []
    for i in text:
        bigletters.append(letters.get(i.lower(),letters[' ']))
    output = ['']*5
    for i in range(5):
        for j in bigletters:
            temp = ' '
            try:
                temp = j[i]
            except:
                pass
            temp += ' '*(5-len(temp))
            temp = temp.replace(' ',' ')
            temp = temp.replace('#','@')
            output[i] += temp
    return '\n'.join(output)
import sys, termios, tty, os, time

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

button_delay = 0.2

kegman = kegman_conf()
#kegman.conf['tuneGernby'] = "1"
#kegman.write_config(kegman.conf)
param = ["tuneGernby", "react", "damp", "Kp", "Ki"]

j = 0
while True:
  print ""
  print ""
  print print_letters(param[j])
  print ""
  print print_letters(kegman.conf[param[j]])
  print ""
  print ("Press 1, 3, 5, 7 to increase by 0.1, 0.05, 0.01, 0.001")
  print ("press a, d, g, j to decrease by 0.1, 0.05, 0.01, 0.001")
  print ("press 0 to make the value 0")
  print ("press 1 to make the value L")
  print ("press SPACE for next parameter")
  print ("press m for previous parameter")
  print ("press q to quit")

  char  = getch()
  if (char == "7"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) + 0.001)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  if (char == "5"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) + 0.01)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == "3"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) + 0.05)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == "1"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) + 0.1)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  if (char == "j"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) - 0.001)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == "g"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) - 0.01)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == "d"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) - 0.05)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)
  elif (char == "a"):
    kegman.conf[param[j]] = str(float(kegman.conf[param[j]]) - 0.1)
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == "0"):
    kegman.conf[param[j]] = "0"
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == "l"):
    kegman.conf[param[j]] = "1"
    kegman.write_config(kegman.conf)
    time.sleep(button_delay)

  elif (char == " "):
    if j < len(param) - 1:
      j = j + 1
    else:
      j = 0

  elif (char == "m"):
    if j > 0:
      j = j - 1
    else:
      j = len(param) - 1

  elif (char == "q"):
    break
