#coding = UTF-8

import hashlib

class b:
    def __init__(self, b, i):
        self.s = b or 0
        self.e = i or 0

class Encypt:

    def encyptPwd(self, password, verifycode, uin):
    
        def md5_hex(s):
            m = hashlib.md5(s)
            return m.hexdigest()

        def md5_bin(s):
            m = hashlib.md5(s)
            return m.digest() 
          
        r = md5_bin(password) + uin 
        r = md5_hex(r)
        r = (r + verifycode).upper()
        r = md5_hex(r).upper()
        return r
    
    def getHash(self, b, j):

        a = j + "password error"
        i = ""
        E = []
        while True:
            if len(i) < len(a):
                i += b
                if len(i) == len(a):
                    break
            else:
                i = i[:len(a)]
                break
        c = 0
        while  c < len(i):
            E.append(ord(i[c]) ^ ord(a[c]))
            c += 1
        a = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
        i = ""
        c = 0
        while c < len(E):
            i += a[E[c] >> 4 & 15 ]
            i += a[E[c] & 15]
            c += 1
        return i

    def getHash2014613225627(self, i, a):

        r = [int(i) >> 24 & 255,int(i) >>16 & 255,int(i) >> 8 & 255,int(i) & 255]
        j = [ord(a[i]) for i in range(len(a))]
        e = [b(0,len(j) - 1)]
        while len(e) > 0:
            """
                var c=e.pop();
            if(!(c.s>=c.e||c.s<0||c.e>=j.length)){
                if(c.s+1==c.e){
                    if(j[c.s]>j[c.e]){
                        var l=j[c.s];
                        j[c.s]=j[c.e];
                        j[c.e]=l;
                    };
                }
            """
            c = e.pop()
            if not (c.s >= c.e or c.s < 0 or c.e >= len(j)):
                if c.s + 1 == c.e:
                    if j[c.s] > j[c.e]:
                        l = j[c.s]
                        j[c.s] = j[c.e]
                        j[c.e] = l
                else:
                    """
                    for(var l=c.s,J=c.e,f=j[c.s];c.s<c.e;){
                        
                    """
                    l = c.s
                    J = c.e
                    f = j[c.s]
                    while c.s < c.e:
                        """
                        for(;c.s<c.e&&j[c.e]>=f;){
                            c.e--,r[0]=r[0]+3&255;
                            
                        }
                        """
                        while c.s < c.e and j[c.e] >= f:
                            c.e -= 1
                            r[0] = r[0] + 3 & 255
    #                        print r

                        #c.s<c.e&&(j[c.s]=j[c.e],c.s++,r[1]=r[1]*13+43&255);
                        if c.s < c.e:                        
                            j[c.s] = j[c.e]
                            c.s += 1
                            r[1] = r[1]*13 + 43 & 255
                        """
                        for(;c.s<c.e&&j[c.s]<=f;){
                            c.s++,r[2]=r[2]-3&255;
                        }
                       """
                        while c.s < c.e and j[c.s] <= f:
                            c.s += 1
                            r[2] = r[2]-3 & 255
                        
                        #c.s<c.e&&(j[c.e]=j[c.s],c.e--,r[3]=(r[0]^r[1]^r[2]^r[3]+1)&255);
                        if c.s < c.e:
                            j[c.e] = j[c.s]
                            c.e -= 1
                            r[3] = (r[0]^r[1]^r[2]^r[3] + 1) & 255
                    j[c.s] = f
    #                print e
                    e.append( b(l, c.s - 1) )
                    e.append( b(c.s + 1, J) )
    #        print len(e)
        j=["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
        e = ""
        for i in range(len(r)):
            e += j[r[i] >> 4 & 15]
            e += j[r[i] & 15]
        return e

    def getHash20140409(self, b, i):

        """
        2014,4,9,13:08:45
        @param b:qq
        @param i:ptwebqq

        """
        a = [0 for ss in range(len(i))]
        for s in range(len(i)):
            a[s%4] ^= ord(i[s])
        """
        var j=["EC","OK"],d=[];
        """
        j = ["EC","OK"]
        d = [0,0,0,0]

        d[0]=int(b)>>24&255^ord(j[0][0])
#        d[1]=b>>16&255^j[0][1]
        d[1]=int(b)>>16&255^ord(j[0][1])
        d[2]=int(b)>>8&255^ord(j[1][0])
        d[3]=int(b)&255^ord(j[1][1])

        j=[]
        j = [0 for ss in range(8)]
        for s in range(8):
            if s%2 == 0:
                j[s]=a[s>>1]
            else:
                j[s]=d[s>>1]

        a=["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]

        d=""

        for s in range(len(j)):
            d+=a[j[s]>>4&15]
            d+=a[j[s]&15]
        return d
            
    def getHash_old(self, b, i):
        """
        @param b:qq
        @param i:ptwebqq
        """
        
        a = []
        s = 0
        for s in range(len(i)):
            if len(a) <= s %4:
                a.insert(s % 4, 0)
            a[s % 4] ^= ord(i[s])

        j = ["EC", "OK"]
        d = [None,None,None,None]
        d[0] = int(b) >> 24 & 255 ^ ord(j[0][0])
        d[1] = int(b) >> 16 & 255 ^ ord(j[0][1])
        d[2] = int(b) >> 8 & 255 ^ ord(j[1][0])
        d[3] = int(b) & 255 ^ ord(j[1][1])
        j = [0 for i in range(8)]
        
        for s in range(8):
            
            if s % 2 == 0:
                j[s] = a[s >> 1]
            else:
                j[s] = d[s >> 1]
        d = ""
        a = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"] 
        for s in range(len(j)):
            d += str(a[j[s] >> 4 & 15])
            d += str(a[j[s] & 15])

        return d 

    def get_gtk(self, skey):

        hash = 5381
        for i in range(len(skey)):
            hash += (hash << 5) + ord(skey[i])

        return hash & 2147483647
    
if "__main__" == __name__:

    test = Encypt()
    print test.get_gtk("@GqJ9ZOwn4")
    #print test.getHash("1234567","4132421351")
    print test.encyptPwd("","!yx03","")
