import "./dropdown.css";
const MenuBox = ({ isOpen }) => {
  return (
    <div className="pages" style={{ display: isOpen ? "flex" : "none" }}>
      <ul>
        <li>
          <button>sign up</button>
        </li>
        <li>
          <button className="login">log in</button>
        </li>
        <div className="hr"></div>
        <li>
          <button className="postHouse">post your house</button>
        </li>
        <li>
          <button>wishlists</button>
        </li>
        <li>
          <button>help</button>
        </li>
      </ul>
    </div>
  );
};

export default MenuBox;
