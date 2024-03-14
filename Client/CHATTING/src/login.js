import service from "@/utils/request";

export function login(data)
{
    return service({
        //url:"localhost:8080/login"
        //method:post
        //data:data
    })
}

export function register(data)
{
    return service({
            //url:"localhost:8080/register"
            //method:post
            //data:data
        }

    )
}
export function ForgetPassword(data)
{
    return service({
            //url:"localhost:8080/ForgetPassword"
            //method:post
            //data:data)
        }
    )}