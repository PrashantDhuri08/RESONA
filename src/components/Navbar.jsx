import React from "react";

function Navbar() {
  return (
    <div className="flex justify-between w-screen items-center bg-nav  h-20 border-b-4">
      <div>
        <ul className="flex list-none ">
          <li className="m-2.5 p-2.5">
            <a>Home</a>
          </li>
          <li className="m-2.5 p-2.5">History</li>
          <li className="m-2.5 p-2.5">Instruction</li>
        </ul>
      </div>

      <button class="cursor-pointer group relative flex gap-1.5 px-10 mx-4 py-2 bg-black bg-opacity-80 text-[#f1f1f1] rounded-2xl hover:bg-opacity-70 transition font-semibold shadow-md">
        Contact
      </button>
    </div>
  );
}

export default Navbar;
