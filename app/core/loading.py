from streamlit.delta_generator import DeltaGenerator


def loading_animation(placeholder: DeltaGenerator, progress: int):

    placeholder.markdown(
        f"""
    <div id="overlay">
        <div id="progress-container">
            <div id="progress-bar"></div>
        </div>
    </div>
    <style>
        #overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        #progress-container {{
            width: 80%;
            height: 20px;
            background-color: #ddd;
            border-radius: 10px;
            overflow: hidden;
        }}
        #progress-bar {{
            width: {progress}%;
            height: 100%;
            background-color: #4CAF50;
            
        }}
        @keyframes grow {{
            0% {{ width: 0%; }}
            100% {{ width: 100%; }}
        }}
        # div[data-testid="stStatusWidget"] div button {{
        # display: none;
        # }}
    </style>
    """,
        unsafe_allow_html=True,
    )
