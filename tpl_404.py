# tpl_404.py

HTML_404_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сторінку не знайдено - 404</title>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family={font_family_serif_encoded}:wght@400;600;700&family={font_family_sans_encoded}:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            /* Змінні Python залишаємо в одинарних дужках, бо їх треба замінити */
            --primary: {primary_color_val};
            --secondary: {secondary_color_val};
            --bg-color: {background_color_val};
            --text-main: {text_color_val};
            --font-sans: '{font_family_sans_val}', sans-serif;
            --font-serif: '{font_family_serif_val}', serif;
            
            --surface: #ffffff;
            --shadow-lg: 0 20px 60px rgba(0,0,0,0.1);
            --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
        }}

        body {{
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: var(--font-sans);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background-image: 
                radial-gradient(at 0% 0%, color-mix(in srgb, var(--primary), transparent 95%), transparent 60%),
                radial-gradient(at 100% 100%, color-mix(in srgb, var(--secondary), transparent 95%), transparent 60%);
        }}

        .container {{
            text-align: center;
            padding: 40px;
            max-width: 600px;
            width: 90%;
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: var(--shadow-lg);
            animation: fadeUp 0.8s var(--ease-out);
        }}

        h1 {{
            font-family: var(--font-serif);
            font-size: 8rem;
            margin: 0;
            line-height: 1;
            color: var(--primary);
            opacity: 0.8;
            text-shadow: 4px 4px 0px rgba(0,0,0,0.05);
            position: relative;
            display: inline-block;
        }}

        /* Анімація для цифри 404 */
        h1::after {{
            content: '404';
            position: absolute;
            top: 0; left: 0;
            color: transparent;
            -webkit-text-stroke: 2px var(--primary);
            opacity: 0.3;
            transform: translate(-4px, -4px);
            z-index: -1;
        }}

        .icon-box {{
            font-size: 4rem;
            color: var(--text-main);
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }}

        h2 {{
            font-family: var(--font-serif);
            font-size: 2rem;
            margin: 10px 0 20px;
            font-weight: 700;
        }}

        p {{
            font-size: 1.1rem;
            color: #64748b;
            margin-bottom: 40px;
            line-height: 1.6;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 16px 32px;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 16px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s var(--ease-out);
            box-shadow: 0 10px 20px color-mix(in srgb, var(--primary), transparent 70%);
        }}

        .btn:hover {{
            transform: translateY(-3px) scale(1.02);
            background: color-mix(in srgb, var(--primary), black 10%);
            box-shadow: 0 15px 30px color-mix(in srgb, var(--primary), transparent 60%);
        }}
        
        .btn:active {{
            transform: scale(0.98);
        }}

        /* ТУТ БУЛА ПОМИЛКА: додано подвійні дужки для keyframes */
        @keyframes fadeUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes float {{
            0% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-15px) rotate(5deg); }}
            100% {{ transform: translateY(0px) rotate(0deg); }}
        }}

        /* ТУТ БУЛА ПОМИЛКА: додано подвійні дужки для media query */
        @media (max-width: 600px) {{
            h1 {{ font-size: 6rem; }}
            h2 {{ font-size: 1.5rem; }}
            .container {{ padding: 30px 20px; }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <div class="icon-box">
            <i class="fa-solid fa-pizza-slice"></i>
        </div>
        <h1>404</h1>
        <h2>Ой! Сторінку не знайдено</h2>
        <p>
            Схоже, що сторінка, яку ви шукаєте, була переміщена, видалена або ніколи не існувала. 
            Але не хвилюйтеся, наше меню все ще на місці!
        </p>
        <a href="/" class="btn">
            <i class="fa-solid fa-house"></i> Повернутися до смачного
        </a>
    </div>

</body>
</html>
"""