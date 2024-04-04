import React from "react";
import "./styles.css";
import Dropdown from "../dropDownMenu/dropdown.jsx";

function Header() {
  return (
    <div className="nav">
      <div className="nav-bar">
        <div className="nav-logo">
          <img src="/Images/myhome logo new.png" alt="logo" />
        </div>
        <div className="nav-links">
          <div className="link2">
            <a href="#">Rent</a>
          </div>
          <div className="link2">
            <a href="#">Buy</a>
          </div>
          <div className="link2">
            <a href="#">Sell</a>
          </div>
        </div>
        <div className="profileDiv">
          <div className="post">
            <a href="#">Post Your House </a>
          </div>
          <div className="language">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="languge1"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418"
              />
            </svg>
          </div>
          <Dropdown />
        </div>
      </div>
      <div className="nav-links2">
        <div className="link4">
          <a href="#"> Anywhere</a>
        </div>
        <div className="link3">
          <a href="#"> Everywhere</a>
        </div>
        <div className="join">
          <div className="link4i">
            <a className="link4i" href="#">
              {" "}
              Location
            </a>
          </div>
          <div className="searchDiv">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="searchbtn"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Header;
