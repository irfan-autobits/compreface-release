export const PlayButton = ({ svgHeight, svgColor, onClick }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      height={svgHeight}
      onClick={onClick}
      viewBox="0 0 24 24"
      fill="none"
    >
      <g id="SVGRepo_bgCarrier" stroke-width="0" />

      <g
        id="SVGRepo_tracerCarrier"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <g id="SVGRepo_iconCarrier">
        {" "}
        <rect width="24" height="24" fill="none" />{" "}
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M3 5.49686C3 3.17662 5.52116 1.73465 7.52106 2.91106L18.5764 9.41423C20.5484 10.5742 20.5484 13.4259 18.5764 14.5858L7.52106 21.089C5.52116 22.2654 3 20.8234 3 18.5032V5.49686Z"
          fill={svgColor}
        />{" "}
      </g>
    </svg>
  );
};

export const PauseButton = ({ svgHeight, svgColor, onClick }) => {
  return (
    <svg
      viewBox="0 0 24 24"
      height={svgHeight}
      onClick={onClick}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
      <g
        id="SVGRepo_tracerCarrier"
        stroke-linecap="round"
        stroke-linejoin="round"
      ></g>
      <g id="SVGRepo_iconCarrier">
        {" "}
        <rect width="24" height="24" fill="white"></rect>{" "}
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M20 5L20 19C20 20.6569 18.6569 22 17 22L16 22C14.3431 22 13 20.6569 13 19L13 5C13 3.34314 14.3431 2 16 2L17 2C18.6569 2 20 3.34315 20 5Z"
          fill={svgColor}
        ></path>{" "}
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M8 2C9.65685 2 11 3.34315 11 5L11 19C11 20.6569 9.65685 22 8 22L7 22C5.34315 22 4 20.6569 4 19L4 5C4 3.34314 5.34315 2 7 2L8 2Z"
          fill={svgColor}
        ></path>{" "}
      </g>
    </svg>
  );
};

export const RemoveSVG = ({ svgHeight, svgColor, onClick }) => {
  return (
    <svg
      viewBox="0 0 24 24"
      fill={svgColor}
      height={svgHeight}
      onClick={onClick}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
      <g
        id="SVGRepo_tracerCarrier"
        stroke-linecap="round"
        stroke-linejoin="round"
      ></g>
      <g id="SVGRepo_iconCarrier">
        {" "}
        <path
          d="M17 12C17 11.4477 16.5523 11 16 11H8C7.44772 11 7 11.4477 7 12C7 12.5523 7.44771 13 8 13H16C16.5523 13 17 12.5523 17 12Z"
          fill={svgColor}
        ></path>{" "}
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M12 23C18.0751 23 23 18.0751 23 12C23 5.92487 18.0751 1 12 1C5.92487 1 1 5.92487 1 12C1 18.0751 5.92487 23 12 23ZM12 20.9932C7.03321 20.9932 3.00683 16.9668 3.00683 12C3.00683 7.03321 7.03321 3.00683 12 3.00683C16.9668 3.00683 20.9932 7.03321 20.9932 12C20.9932 16.9668 16.9668 20.9932 12 20.9932Z"
          fill={svgColor}
        ></path>{" "}
      </g>
    </svg>
  );
};

export const AddNew = ({ svgHeight, svgColor, onClick }) => {
  return (
    <svg
      fill={svgColor}
      height={svgHeight}
      onClick={onClick}
      stroke={svgColor}
      version="1.1"
      id="Capa_1"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="-1.68 -1.68 31.32 31.32"
    >
      <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
      <g
        id="SVGRepo_tracerCarrier"
        stroke-linecap="round"
        stroke-linejoin="round"
      ></g>
      <g id="SVGRepo_iconCarrier">
        {" "}
        <g>
          {" "}
          <g id="c140__x2B_">
            {" "}
            <path d="M13.98,0C6.259,0,0,6.26,0,13.982s6.259,13.981,13.98,13.981c7.725,0,13.983-6.26,13.983-13.981 C27.963,6.26,21.705,0,13.98,0z M21.102,16.059h-4.939v5.042h-4.299v-5.042H6.862V11.76h5.001v-4.9h4.299v4.9h4.939v4.299H21.102z "></path>{" "}
          </g>{" "}
          <g id="Capa_1_9_"> </g>{" "}
        </g>{" "}
      </g>
    </svg>
  );
};

export const CloseSvg = ({ svgHeight, svgColor, onClick }) => {
  return (
    <svg
      fill={svgColor}
      height={svgHeight}
      onClick={onClick}
      stroke={svgColor}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
      <g
        id="SVGRepo_tracerCarrier"
        stroke-linecap="round"
        stroke-linejoin="round"
      ></g>
      <g id="SVGRepo_iconCarrier">
        {" "}
        <path
          d="M20.7457 3.32851C20.3552 2.93798 19.722 2.93798 19.3315 3.32851L12.0371 10.6229L4.74275 3.32851C4.35223 2.93798 3.71906 2.93798 3.32854 3.32851C2.93801 3.71903 2.93801 4.3522 3.32854 4.74272L10.6229 12.0371L3.32856 19.3314C2.93803 19.722 2.93803 20.3551 3.32856 20.7457C3.71908 21.1362 4.35225 21.1362 4.74277 20.7457L12.0371 13.4513L19.3315 20.7457C19.722 21.1362 20.3552 21.1362 20.7457 20.7457C21.1362 20.3551 21.1362 19.722 20.7457 19.3315L13.4513 12.0371L20.7457 4.74272C21.1362 4.3522 21.1362 3.71903 20.7457 3.32851Z"
          fill="#fff"
        ></path>{" "}
      </g>
    </svg>
  );
};
