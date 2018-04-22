
__author__ = 'akashmalla'

import numpy as np
import sys

cleanedinput=[]
users=[]
movies=[]

#Read each line of input data and remove whitespaces and exit program if user input provided is wrong values.
#Also, skip any lines starting with '#'
for line in sys.stdin:
    print(line.rstrip())
    if not line.startswith('#'):
        cleanedline = line.strip()
        if cleanedline:
            x = cleanedline.split(' ')
            if x[0].strip().isdigit() and x[1].strip().isdigit() and float(x[2].strip())>0 and float(x[2].strip())<=5 and len(x)==3:
                u = int(x[0].strip())
                m = int(x[1].strip())
                cleanedinput.append([float(x.strip()) for x in cleanedline.split(',')])
                if u not in users:
                    users.append(u)
                if m not in movies:
                    movies.append(m)
            else:
                sys.exit('Wrong input given to program. User id and Movie id has to be integers and Rating has to be a float')

#Sort all unique movies and user ids in ascending order
movies.sort()
users.sort()

#Create a m by m matrix where m is the number of unique movies all initialized to 0
matrix = np.zeros(len(movies)**2,dtype='int64').reshape(len(movies),len(movies))

#Change the cleanedinput to numpy array where first 2 columns are integers and third column is float
inputarray = np.array(cleanedinput,dtype=object)
inputarray[:,0:2] = inputarray[:,0:2].astype(int)

#Sort input data by user ids
input=sorted(inputarray,key=lambda x: x[0])

moviesperuser = [[i[1] for i in input if i[0]==u] for u in users]
print(moviesperuser)
subusermovies=[]

#Below will build the co-occurrence matrix by going over all movies watched per user
for mpu in moviesperuser:
    subusermovies=mpu.copy()
    for m in mpu:
        for n in subusermovies:
            if m != n:
                matrix[movies.index(m),movies.index(n)]+=1
                matrix[movies.index(n),movies.index(m)]+=1
            else:
                matrix[movies.index(m),movies.index(n)]+=1
            #print(m,n,i[0]-1) This print helped debug problems.
        subusermovies.remove(m)

print('\nCo-occurrence Matrix:')
print(matrix)

#Build a list of each user ratings provided to movies they watched
userratings = [[0 for i in range(len(movies))] for u in users]
for u in users:
    for i in input:
        if i[0]==u:
            for m in movies:
                if i[1]==m:
                    userratings[users.index(u)][movies.index(m)]=i[2]

print('\nUser Ratings matrix (0 for a movie not watched):')
print(userratings)

print('\nCo-occurrence Results:')
#Compute dot product of co-occurrence matrix and each user ratings matrix, then choose the
#biggest number from the output matrix for which the user has not watched the movie.
recommendation=0
for ur in userratings:
    result=np.dot(matrix,ur)
    subresult=[]
    for m in range(len(movies)):
        if ur[m]==0:
            subresult.append(result[m])
            if result[m] == max(subresult):
                recommendation=movies[m]
    print('user ',str(userratings.index(ur)+1),':',subresult,', the recommended movie is ',recommendation)

#User-based efficient algorithm
print('\nUser-based Efficient Algorithm Results:')
similarity= [[0 for i in range(len(users)-1)] for u in users]
sim={}
pick=1
possiblerecommendations={}

for u in users:
    i=0
    j=0
    for w in users:
        if u != w:
            topAll=[]
            u1=[]
            u2=[]
            twouserratings = [[0 for i in range(2)] for m in movies]
            for m in movies:
                #If both user u and user w have watched movie m, then we update twouserratings matrix with that movie rating
                if userratings[users.index(u)][movies.index(m)] != 0 and userratings[users.index(w)][movies.index(m)] != 0:
                    twouserratings[movies.index(m)][0]=userratings[users.index(u)][movies.index(m)]
                    twouserratings[movies.index(m)][1]=userratings[users.index(w)][movies.index(m)]
                    #Below matrix is appended to calculate similarity
                    topAll.append(twouserratings[movies.index(m)][0]*twouserratings[movies.index(m)][1])
                if userratings[users.index(u)][movies.index(m)] == 0 and userratings[users.index(w)][movies.index(m)] != 0:
                    #Possible recommendations matrix will hold all movie recommendations possible to recommend user u
                    possiblerecommendations[str(u)+str(j)]=[userratings[users.index(w)][movies.index(m)],m,w]
                    j+=1
            #Below will compute cosine similarity between user u and user w
            for ur in twouserratings:
                u1.append(ur[0]**2)
                u2.append(ur[1]**2)
            s1=sum(u1)
            s2=sum(u2)
            bottom=np.sqrt(s1)*np.sqrt(s2)
            top=sum(topAll)
            if bottom != 0:
                sim[str(u)+str(w)]=top/bottom
                similarity[users.index(u)][i]=top/bottom
                i+=1
    #Sort similarity matrix in descending order and choose the top 25% neighbhors
    similarity[users.index(u)].sort(reverse=True)
    pick=round(len(similarity[users.index(u)])*0.25)
    b=0
    numloop=(len(users)-1)*(len(movies)-1)
    compute={}
    d=1
    for uid,s in sim.items():
        for p in range(pick):
            if s == similarity[users.index(u)][p]:
                #print('uid: ',uid,u)
                for c in range(numloop):
                    if possiblerecommendations.get(str(u)+str(c),'none') != 'none':
                        #If the second character or digit of uid is equal to the user id (other user) in possiblerecommendations,
                        #then we need to look at all of those user's movie ratings
                        if possiblerecommendations[str(u)+str(c)][2]==int(uid[1:]):
                            #In the top 25% similarities, if we get more than 1, then we need to add the top similarities and divide
                            #by the total number of similarities.
                            if possiblerecommendations[str(u)+str(c)][1] in compute:
                                compute[possiblerecommendations[str(u)+str(c)][1]]+=s*possiblerecommendations[str(u)+str(c)][0]
                                d+=1
                                if d==p:
                                    compute[possiblerecommendations[str(u)+str(c)][1]]/=d
                            else:
                                compute[possiblerecommendations[str(u)+str(c)][1]]=s*possiblerecommendations[str(u)+str(c)][0]
                            #print(possiblerecommendations[str(u)+str(c)])

    #print(compute)
    #If compute has data, in other words, if there is some user who has watched a movies that user u
    #has not watched, then this will recommend the best movie. If compute has no data, then there is
    #no other user in input data that has watched a movie that user u has not watched, so recommend none.
    if compute:
        print('user',u,': the recommended movie is ',max(compute, key=compute.get))
    else:
        print('user',u,': the recommended movie is none')
