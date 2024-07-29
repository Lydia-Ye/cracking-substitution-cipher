"""
hw4.py
Name: Lydia Ye
Date: March 13, 2024
"""


import numpy as np
import random
import string

'''
Randomly permute the alphabet
'''
def permute_alphabet(alphabet):
    permutation = alphabet.copy()
    random.shuffle(permutation)
    return permutation

'''
Encipher a message using a given cipher
'''
def encipher_message(message, cipher, alphabet):
    # ignore  any characters not in the alphabet
    message = ''.join(filter(lambda ch: ch in alphabet, message))
    enciphered_message = ''
    #  replace each letter of the message with the corresponding letter in the cipher
    for char in message:
        enciphered_message += cipher[alphabet.index(char)]

    return enciphered_message


'''
Generate a new reverse cipher Y given a current reverse cipher X by randomly select- ing two letters and swapping them
'''
def generate_new_cipher(cipher):
    # Make a copy of the current cipher
    new_cipher = cipher.copy()
    
    # randomly selecting two letters and swapping them.
    i, j = random.sample(range(len(new_cipher)), 2)
    new_cipher[i], new_cipher[j] = new_cipher[j], new_cipher[i]
    
    return new_cipher


'''
Create the transition matrix M
'''
def create_transition_matrix(fileName, alphabet):
    # Initialize transition matrix and transition counts
    transition_matrix = np.zeros((len(alphabet), len(alphabet)))
    transition_counts = {}
    total_counts = 0

    # Initialize all possible transitions with 0
    for char1 in alphabet:
        for char2 in alphabet:
            transition_counts[(char1, char2)] = 0
    
    # Read the file and get the content
    file = open(fileName, "r")
    content = file.read()
    content = ''.join(filter(lambda ch: ch in alphabet, content))
    file.close()

    # Record the transition counts
    for i in range(len(content) - 1):
        char1, char2 = content[i], content[i + 1]
        transition_counts[(char1, char2)] += 1
        total_counts += 1

    # Fill the transition matrix with the probabilities
    for (char1, char2), count in transition_counts.items():
        i, j = alphabet.index(char1), alphabet.index(char2)
        transition_matrix[i][j] = count / total_counts

    # Replace all zeros with 1e-20
    transition_matrix[transition_matrix == 0] = 1e-20

    return transition_matrix

'''
Calculate the log probability for a given cipher
'''
def compute_log_probability(cipher, transition_matrix, message, alphabet):
    M = transition_matrix
    unscrambled_message = encipher_message(message, cipher, alphabet)
    log_probability = sum(np.log(M[alphabet.index(unscrambled_message[i])][ alphabet.index(unscrambled_message[i+1])])
                          for i in range(len(unscrambled_message) - 1))
    
    probability = sum(M[alphabet.index(unscrambled_message[i])][ alphabet.index(unscrambled_message[i+1])]
                          for i in range(len(unscrambled_message) - 1))

    return log_probability

'''
Calculate the acceptance probability for the proposed move from X to Y
'''
def compute_acceptance(log_P_x, log_P_y):
    if log_P_y > log_P_x:
        return 1
    else:
        acceptance_probability = np.exp(log_P_y - log_P_x)

    return acceptance_probability



'''
Generate the chain of 10,000 reverse ciphers using Metropolis-Hastings.
'''
def metropolis_hastings(transition_matrix, message, alphabet, iterations=10000):
    initial_cipher = permute_alphabet(alphabet)
    best_cipher = initial_cipher
    best_log_P = compute_log_probability(initial_cipher, transition_matrix, message, alphabet)
    x = initial_cipher
    
    for _ in range(iterations):
        y = generate_new_cipher(x)
        log_P_x = compute_log_probability(x, transition_matrix, message, alphabet)
        log_P_y = compute_log_probability(y, transition_matrix, message, alphabet)
        acceptance = compute_acceptance(log_P_x, log_P_y)

        if best_log_P < log_P_y:
            best_cipher = y
            best_log_P = log_P_y
        
        # If the proposed cipher is accepted, update the x
        if random.random() <= acceptance:
            x = y

    return best_cipher


'''
Part 2 Tricking the Metropolis hasting

The first way I came up is to insert extra letters in between each other two letters in the
original message before substitution. The main idea of this is to make some uncommon pairs manually
and break the actual letter pairs we have in the original message. Specifically, to implement this, 
we can insert characters according to the order in the alphabet in between each pair of letter. For 
example, consider a string "Hello", there are 4 spots in between each letter pairs in this message. 
So, we start by putting the first element taken from the alphabet into the first spot, putting the 
second element from the alphabet into the second spot and so on. After this operation, we will
have a new string with roughly double the length of original string and for this string, we will get
"Haeblcldo" as the modified version. To reverse this change, we can simply take out all the letters 
at the odd index (starting from 0) in the modified string. 
    
I expect this to significantly decrease the measure, because it adds many unconventional letter 
pairs to the dataset, which may lead to very low score even when the reverse cipher works correctly. 
However, this method might be relatively less efficient, because we will need to add many additonal 
letters and double the size of the original message.

The second way is to delete the space after every two words. That is, we start by taking out the first space
after the first two words, then the first space after the first four words, and so on. For an example 
message "This is a example for deleting the spaces in the message.", the operation will return the message
"This isa examplefor deletingthe spacesin themessage." This should be able to interrupt with the normal
probablity of letter pairs in the similar way as the first method does. 
    
In general, this way should be easy to implement as we only need to search for the spaces in the messeage
and delete some of them accordingly. Also, this operation does not need additional memory for making the 
message longer with extra letters. However, it is harder to recover this message because the user need
to infer where exactly in certain words we should put the missing space at. On the other hand, this might 
also increase the security because in order to recover the original message, the metropolis attacker must
create a reverse cipher as accurate as possible, otherwise, it is difficult to infer the deletion location.

To compare this two methods, the first way in increasing the security than the second way. However, it
takes much longer runtime when actually implementing it. So, the second way might be perform better in
the case of efficient security. 
    
'''


'''
Alter the message using insertion method
'''
def insert_extra_letter(original_message, alphabet):
    modified_message = ""  

    for i in range(len(original_message)):
        modified_message += original_message[i]  # Add the original letter
        if i < len(original_message) - 1:  
            # Add the alphabet letter to the modified message
            modified_message += alphabet[i % len(alphabet)]

    return modified_message


'''
Recover the message from the insertion modification
'''
def recover_insertion(modified_message):
    # Take out every second letter starting from the first (0 index)
    original_message = modified_message[::2]
    return original_message



"""
main function
"""
if __name__ == '__main__':
    # Define the alphabet as a string to include all lower case letters, all upper case letters, 
    # the space character, the comma character, and the period character
    original_alphabet_str = string.ascii_lowercase + string.ascii_uppercase + ' ,.'
    original_alphabet = list(original_alphabet_str)

    # Create the transition matrix and save it to a text file
    M = create_transition_matrix("WarAndPeace.txt", original_alphabet)
    np.savetxt('transition_matrix.txt', M)
    # Load the transition matrix file
    M = np.loadtxt('transition_matrix.txt')

    # Example of cipher used to scramble the text
    test_cipher_str = ' ,.' + string.ascii_lowercase + string.ascii_uppercase
    test_cipher = list(test_cipher_str)


    print("------------------ Part 1 --------------------\n")

    # Example scrambled text
    original_text = open("test_text.txt", "r", encoding="utf-8").read()
    scrambled_text = encipher_message(original_text, test_cipher, original_alphabet)

    # Apply the Metropolis-Hastings algorithm
    reverse_cipher = metropolis_hastings(M, scrambled_text, original_alphabet)

    # Unscramble the text using the obtained reverse cipher alphabet
    unscrambled_text = encipher_message(scrambled_text, reverse_cipher, original_alphabet)

    # Print info
    print("Original Alphabet: " + original_alphabet_str + "\n")
    print("Cipher: " + test_cipher_str + "\n")
    print("Reverse Cipher: " + ''.join(reverse_cipher) + "\n")
    print("Unscrambled Text: " + unscrambled_text + "\n")



    print("------------------ Part 2 --------------------")
    # Example scrambled text, modified before substitution
    original_text = open("test_text.txt", "r", encoding="utf-8").read()
    modified_text = insert_extra_letter(original_text, original_alphabet)
    scrambled_text = encipher_message(modified_text, test_cipher, original_alphabet)

    # Apply the Metropolis-Hastings algorithm
    reverse_cipher = metropolis_hastings(M, scrambled_text, original_alphabet)

    # Unscramble the text using the obtained reverse cipher alphabet
    unscrambled_text = encipher_message(scrambled_text, reverse_cipher, original_alphabet)
    recovered_text_from_modification = recover_insertion(unscrambled_text)

    # Print info
    print("Original Alphabet: " + original_alphabet_str + "\n")
    print("Cipher: " + test_cipher_str + "\n")
    print("Reverse Cipher: " + ''.join(reverse_cipher) + "\n")
    print("Modified Text with Extra Letters: " + modified_text + "\n")
    print("Unscrambled Text: " + unscrambled_text + "\n")
    print("Unscrambled Text Recover From Modification: " + recovered_text_from_modification + "\n")

    '''
    For the first part, the algorithm can return a mostly correct reverse cipher at the most time. 
    Usually, the mapping for lowercase letters are closer to the mapping in the correct reverse cipher 
    than the mapping for capitalized letters, because there are less data for capitalized letter from
    the message. 

    For the second part, the algorithm takes significantly longer  time to finish the 10000 iterations 
    and the modification before substitution successfully prevent the algorithm to find out the correct
    reverse cipher. This method of modifying the message can significantly improve the security, but it 
    is not very efficient.
    '''