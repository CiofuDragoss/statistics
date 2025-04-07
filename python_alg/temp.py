# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 19:27:20 2024

@author: drago
"""

import re
def organize_archive(mail:list[list[str]],hash_func:str,command:str)->tuple[list[list[str]],int]:
    
    if not mail or len(mail[0])==0 or not hash_func or not command:
        raise ValueError("Empty input.")
    
    #first HELPER FUNCTIONS, to help build the archive and the folders
    #get the size of the archive, n
    def get_size_of_archive(hash_func):
         match_mod= r"^\(\d+\+x\+\d+\)%(\d+)$"
         match=re.search(match_mod,hash_func)
        #error if hash_func has no %integer
         if not match:
             raise ValueError("Invalid hash_func.")
         return int(match.group(1))
    #get the id of either category or message, using number, a regex pattern.
    def get_id(text):
        number=r'^(\d+)'
        
        identification=re.search(number,text)
        #error if there is no index
        if not identification:
            raise ValueError("Invalid mail stack.")
        return int(identification.group())
    
    #compute, for getting the position of a specific item in the archive/folder
    def calculate_hash_func(x,hash_func):
        hash_func=hash_func.replace("x",str(x))
        return eval(hash_func)
    
    #generate the folders
    def generate_folders(archive,mail,hash_func):
        #folder_archive
        folder_archive=[]
        #each category is a box, divided if needed (more categories in the same box)
        for box in archive:
            for category in box:
                folder=[[] for _ in range(len(archive))]
                iterate=0
                #we go through the mail stack and reduce its size each time we put a letter in a
                #specific category 
                while(iterate!=len(mail)):
                    if mail[iterate][0]==category:
                        message_id=get_id(mail[iterate][1])
                        position=calculate_hash_func(message_id,hash_func)
                        folder[position].append(mail[iterate][1])
                        del mail[iterate]
                        iterate-=1
                    iterate+=1
                #sort the category's folder, then add it to the big archive
                for sub_folder in folder:
                    sub_folder.sort(key=get_id)
                    
                    
                folder_archive.append(folder.copy())
        return folder_archive
        
                    
    #initialize the archive and categories
    archive=[]
    categories=[]
    archive=[[]for _ in range(get_size_of_archive(hash_func))]
        
    #create the archive 
    for letter in mail:
        position=calculate_hash_func(get_id(letter[0]),hash_func)
        
        if letter[0] not in categories:
            get_id(letter[0]) #error checking
            categories.append(letter[0])
            archive[position].append(letter[0])
    #arrange the categories in the box (if in the box there are more categories)
    for letter in archive:
        letter.sort(key=get_id)
    
    #get the folder_archive. Now you built the king his efficient archive!
    folder_archive=generate_folders(archive,mail,hash_func)
    #we will use categories to make the connection to the folder of a specific category in the folder_archive
    #we will rebuild the categories array,tracking the 'order' of each category in the archive.
    categories = [i for row in archive for i in row]
    
    #Second HELPER FUNCTIONS, to help process the king's command, and return the efficiency for the command
    #and the archive (we will also process the archive so that it shows without numbers to the king)
    
    
    #get the presentation variant of the archive
    def process_archive(archive):
        return [[re.sub(r'^\d+\s*','', category).strip() for category in box] for box in archive]
    
    #understand what the king wants
    def process_command(command):
        valid_command = r"Tobuk ,I want the mail containing:\s*(.+?)\.Coming from\s+(.+)$"
        processed_command=re.search(valid_command,command)
        if not processed_command:
            raise ValueError("Invalid command.")
        #return category, message
        return processed_command.group(2),processed_command.group(1)
    
    #show the king the archive efficiency
    def moves(archive,folder_archive,hash_func,categories,category,message):
        moves=0
        found=False
        category_id=get_id(category)
        message_id=get_id(message)
        position_of_category=calculate_hash_func(category_id, hash_func)
        position_of_message=calculate_hash_func(message_id, hash_func)
        #first find the category
        for cat in archive[position_of_category]:
            moves+=1
            if cat==category:
                found=True
                break
        #if we don't find the category in the archive, error
        if not found:
            raise ValueError("Invalid command.")
        found=False
        #imagine this like Tobuk is looking at a piece of paper (categories) to find the relation between
        #the folder_archive and archive. He knows the index of the folder for a specific category
        # by looking at the categories array.
        position_of_folder = next(
    (i for i in range(len(categories)) if get_id(categories[i]) == get_id(category))
  )
        #look in the folder_archive, at the folder found at position_of_folder, and the position_of_message
        #this is a 3d list.Now check where is the messege located, increment moves each time.
        for mess in folder_archive[position_of_folder][position_of_message]:
            moves+=1
            if mess==message:
                found=True
                break
        if not found:
            raise ValueError("Invalid command.")
        return moves
    #call second helper functions to return
    
    category,message=process_command(command)
    return (process_archive(archive),moves(archive,folder_archive,hash_func,categories,category,message))


mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      ["10 Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+x+2)%10"
command="Tobuk ,I want the mail containing: 6dPUPPPP.Coming from 3 Secret"
expected=([[], [], [], ['Random'], [], [], ['Secret'], [], ['Red kingdom'], ['Blue kingdom']], 2)
assert(organize_archive(mail,hash_func,command))==expected

mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      ["10 Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+x+2)%2"
command="Tobuk ,I want the mail containing: 6dPUPPPP.Coming from 3 Secret"
expected=([['Secret', 'Red kingdom'], ['Blue kingdom', 'Random']], 4)
assert(organize_archive(mail,hash_func,command))==expected


mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      ["10 Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+x+4321)%3"
command="Tobuk ,I want the mail containing: 1I'm a joker , I want to serve your kingdom.Coming from 10 Random"
expected=([['Random'], ['Red kingdom'], ['Secret', 'Blue kingdom']], 2)
assert(organize_archive(mail,hash_func,command))==expected

mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      ["10 Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+x+4321)%3"
command="Tobuk ,I want the mail containing: 1I'm a joker , I want to serve your kingdom.Coming from 10 Rando"
try:
    result=organize_archive(mail,hash_func,command)
    assert False
except ValueError as e:
    assert str(e)=="Invalid command."

mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      [" Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+x+4321)%3"
command="Tobuk ,I want the mail containing: 1I'm a joker , I want to serve your kingdom.Coming from 10 Random"
try:
    result=organize_archive(mail,hash_func,command)
    assert False
except ValueError as e:
    assert str(e)=="Invalid mail stack."
    
mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      ["10 Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+x+4321)%3"
command="Tok ,I want the mail containing: 1I'm a joker , I want to serve your kingdom.Coming from 10 Random"
try:
    result=organize_archive(mail,hash_func,command)
    assert False
except ValueError as e:
    assert str(e)=="Invalid command."
    
mail=[]
hash_func="(1+x+4321)%3"
command="Tok ,I want the mail containing: 1I'm a joker , I want to serve your kingdom.Coming from 10 Random"
try:
    result=organize_archive(mail,hash_func,command)
    assert False
except ValueError as e:
    assert str(e)=="Empty input."
    
    
    
mail=[["5 Red kingdom","1The army needs strength"],
      ["5 Red kingdom","2The army needs more strength"],
      ["5 Red kingdom","3The army needs more,more, AND strength"],
      ["6 Blue kingdom","1Hello old friend"],
      ["3 Secret","1sdadasdsa dsa asdas dsa das ds"],
      ["3 Secret", "2sadsadsdas dsad as das dsa das sdsd as das dsa"],
      ["3 Secret", "3PUP"],
      ["3 Secret", "4PUPPP"],
      ["3 Secret", "5PUPPPP"],
      ["3 Secret", "6dPUPPPP"],#the king wants this one
      ["10 Random", "1I'm a joker , I want to serve your kingdom"]]
hash_func="(1+xze+4321)%3"
command="Tobuk ,I want the mail containing: 1I'm a joker , I want to serve your kingdom.Coming from 10 Random"
try:
    result=organize_archive(mail,hash_func,command)
    assert False
except ValueError as e:
    assert str(e)=="Invalid hash_func."
