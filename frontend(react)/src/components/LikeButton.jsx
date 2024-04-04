import { useState } from "react"

const LikeButton = () =>{
    const [like, setLike]= useState(true);
    const toggleLike = ()=> setLike(!like);
    return(
        <button className="favDiv" onClick={toggleLike}>
            <img className="favourite" src={like ? "./Images/plain.svg" : "./Images/liiked.svg" }  alt="" />
        </button>
    )
}

export default LikeButton



