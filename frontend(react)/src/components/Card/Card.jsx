import { HOMES } from "../../assets/data/homes";
import "./style.css";
import React from "react";
import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css";
import LikeButton from "../LikeButton";

export default function Card() {
  return (
    <>
      {HOMES.map((home, index) => (
        <div  className="singleCard">
          <div>
                  <LikeButton/>
                </div>
          <Carousel className="carouselImg">
            {home.value.images.map((img) => (
              <div key={index}>
                
                <img src={img} alt="" />
              </div>
            ))}
          </Carousel>
          <div className="infoDiv">
            <div className="location">
              <p className="pmain">{home.value.location}</p>
              <p className="p2">{home.value.address}</p>
              <p>&#8358; {home.value.amount}</p>
            </div>
            <div className="rating">
              <div className="star">
                <img src="./Images/Star 1.svg" alt="" />
              </div>

              <p>{home.value.rating}</p>
            </div>
          </div>
        </div>
      ))}
    </>
  );
}
