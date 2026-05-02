from core.AppException import AppException






def createUser(client,user):
    try : 
        newUser = client.table("users").upsert({"id":user["sub"], "email":user.get("email")}).execute()

    except Exception as e:
         raise AppException(f"Error while creation {e}",500)
    
    return newUser.data[0]


def getUser(client,id): 
        user  = client.table("users").select("*").eq("id",id).execute()

        if not user.data :
            raise AppException(f"User doesn't exist",404)

        return user.data[0]



def updateUser(client,id,userData):
   
    try : 
        user  = client.table("users").update(userData).eq("id",id).execute()

    except:
         raise AppException(f"Error During user update",500)

    if not user.data :
        raise AppException(f"User doesn't exist",404)
    
    return user.data[0]