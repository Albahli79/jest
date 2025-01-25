<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Paint Estimation & Labor Cost Calculator</title>
  <style>
    body { 
      font-family: 'Aptos', sans-serif; 
      background: #f4f4f4; 
      color: #333; 
      margin: 0; 
      padding: 0; 
    }
    .container { 
      max-width: 800px; 
      margin: 50px auto; 
      padding: 20px; 
      background: #fff; 
      border-radius: 8px; 
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); 
    }
    h1 { 
      text-align: center; 
      color: #2c3e50; 
    }
    .language-selector { 
      text-align: right; 
      margin-bottom: 20px; 
    }
    .buttons { 
      display: flex; 
      justify-content: center; 
      gap: 20px; 
      margin-bottom: 30px; 
    }
    button { 
      padding: 15px 30px; 
      background: #2c3e50; 
      color: #fff; 
      border: none; 
      border-radius: 4px; 
      cursor: pointer; 
      font-size: 16px; 
    }
    button:hover { 
      background: #1a252f; 
    }
    label { 
      display: block; 
      margin: 10px 0 5px; 
    }
    input, select { 
      width: 100%; 
      padding: 10px; 
      margin-bottom: 15px; 
      border: 1px solid #ccc; 
      border-radius: 4px; 
    }
    .output { 
      margin-top: 20px; 
      padding: 15px; 
      background: #e9f7ff; 
      border-radius: 4px; 
    }
    /* T3lm: Protect rights and ideas */
    .t3lm { 
      display: none; 
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="language-selector">
      <select id="language">
        <option value="en">English</option>
        <option value="ar">Arabic</option>
        <option value="ur">Urdu</option>
        <option value="hi">Hindi</option>
        <option value="bn">Bengali</option>
      </select>
    </div>
    <h1 id="title">Paint Estimation & Labor Cost Calculator</h1>
    <div class="buttons">
      <button id="villaButton">Villa</button>
      <button id="roomButton">Room</button>
    </div>
  </div>

  <div class="t3lm">T3lm</div>

  <script>
    const translations = {
      en: {
        title: "Paint Estimation & Labor Cost Calculator",
        villaButton: "Villa",
        roomButton: "Room"
      },
      ar: {
        title: "حاسبة تقدير الطلاء وتكلفة العمالة",
        villaButton: "فيلا",
        roomButton: "غرفة"
      }
      // Add translations for Urdu, Hindi, and Bengali here.
    };

    function updateLanguage() {
      const lang = document.getElementById('language').value;
      const elements = translations[lang];
      for (const key in elements) {
        document.getElementById(key).textContent = elements[key];
      }
      document.body.style.fontFamily = lang === 'ar' ? 'Simplified Arabic' : 'Aptos, sans-serif';
    }

    document.getElementById('language').addEventListener('change', updateLanguage);
    updateLanguage(); // Initialize language

    document.getElementById('villaButton').addEventListener('click', () => {
      window.location.href = 'villa.html';
    });

    document.getElementById('roomButton').addEventListener('click', () => {
      window.location.href = 'room.html';
    });
  </script>
</body>
</html>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Villa Paint Estimation</title>
  <style>
    /* Same styles as homepage */
  </style>
</head>
<body>
  <div class="container">
    <h1 id="title">Villa Paint Estimation</h1>
    <form id="villaForm">
      <label for="interiorWalls" id="interiorWallsLabel">Total Meters for Interior Walls:</label>
      <input type="number" id="interiorWalls" step="0.1" required>
      
      <label for="externalWalls" id="externalWallsLabel">Total Meters for External Walls:</label>
      <input type="number" id="externalWalls" step="0.1" required>
      
      <label for="ceilings" id="ceilingsLabel">Total Meters for Ceilings:</label>
      <input type="number" id="ceilings" step="0.1" required>
      
      <label for="additionalMeters" id="additionalMetersLabel">Additional Meters (Optional):</label>
      <input type="number" id="additionalMeters" step="0.1">
      
      <label for="laborPrice" id="laborPriceLabel">Labor Price per Meter (Optional, SAR):</label>
      <input type="number" id="laborPrice" step="0.1">
      
      <label for="paintPrice" id="paintPriceLabel">Paint Price per Meter (Optional, SAR):</label>
      <input type="number" id="paintPrice" step="0.1">
      
      <button type="button" onclick="calculateVilla()" id="calculateButton">Calculate</button>
    </form>
    
    <div class="output" id="output">
      <p>Total Output: <span id="totalOutput">0</span> m²</p>
      <p>Total Labor Price: <span id="totalLaborPrice">0</span> SAR</p>
      <p>Total Paint Required: <span id="totalPaint">0</span> liters</p>
      <p>Total Paint Volumes (16L Cans): <span id="totalPaint16L">0</span></p>
      <p>Total Paint Volumes (3L Cans): <span id="totalPaint3L">0</span></p>
    </div>
  </div>

  <script>
    function calculateVilla() {
      const interiorWalls = parseFloat(document.getElementById('interiorWalls').value) || 0;
      const externalWalls = parseFloat(document.getElementById('externalWalls').value) || 0;
      const ceilings = parseFloat(document.getElementById('ceilings').value) || 0;
      const additionalMeters = parseFloat(document.getElementById('additionalMeters').value) || 0;
      const laborPrice = parseFloat(document.getElementById('laborPrice').value) || 0;
      const paintPrice = parseFloat(document.getElementById('paintPrice').value) || 0;

      const totalOutput = interiorWalls + externalWalls + ceilings + additionalMeters;
      const totalLaborPrice = totalOutput * laborPrice;
      const totalPaint = totalOutput / 13;
      const totalPaint16L = Math.ceil(totalPaint / 16);
      const totalPaint3L = Math.ceil(totalPaint / 3);

      document.getElementById('totalOutput').textContent = totalOutput.toFixed(2);
      document.getElementById('totalLaborPrice').textContent = totalLaborPrice.toFixed(2);
      document.getElementById('totalPaint').textContent = totalPaint.toFixed(2);
      document.getElementById('totalPaint16L').textContent = totalPaint16L;
      document.getElementById('totalPaint3L').textContent = totalPaint3L;
    }
  </script>
</body>
</html>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Room Paint Estimation</title>
  <style>
    /* Same styles as homepage */
  </style>
</head>
<body>
  <div class="container">
    <h1 id="title">Room Paint Estimation</h1>
    <form id="roomForm">
      <label for="length" id="lengthLabel">Length of the Wall (m):</label>
      <input type="number" id="length" step="0.1" required>
      
      <label for="width" id="widthLabel">Width of the Wall (m):</label>
      <input type="number" id="width" step="0.1" required>
      
      <label for="height" id="heightLabel">Height of the Wall (m):</label>
      <input type="number" id="height" step="0.1" required>
      
      <label for="doors" id="doorsLabel">Number of Doors:</label>
      <input type="number" id="doors" step="1">
      
      <label for="windows" id="windowsLabel">Number of Windows:</label>
      <input type="number" id="windows" step="1">
      
      <label for="laborPrice" id="laborPriceLabel">Labor Price per Meter (Optional, SAR):</label>
      <input type="number" id="laborPrice" step="0.1">
      
      <label for="paintPrice" id="paintPriceLabel">Paint Price per Meter (Optional, SAR):</label>
      <input type="number" id="paintPrice" step="0.1">
      
      <button type="button" onclick="calculateRoom()" id="calculateButton">Calculate</button>
    </form>
    
    <div class="output" id="output">
      <p>Total Output: <span id="totalOutput">0</span> m²</p>
      <p>Total Labor Price: <span id="totalLaborPrice">0</span> SAR</p>
      <p>Total Paint Required: <span id="totalPaint">0</span> liters</p>
      <p>Total Paint Volumes (16L Cans): <span id="totalPaint16L">0</span></p>
    </div>
  </div>

  <script>
    function calculateRoom() {
      const length = parseFloat(document.getElementById('length').value) || 0;
      const width = parseFloat(document.getElementById('width').value) || 0;
      const height = parseFloat(document.getElementById('height').value) || 0;
      const doors = parseFloat(document.getElementById('doors').value) || 0;
      const windows = parseFloat(document.getElementById('windows').value) || 0;
      const laborPrice = parseFloat(document.getElementById('laborPrice').value) || 0;
      const paintPrice = parseFloat(document.getElementById('paintPrice').value) || 0;

      const totalArea = (length * height * 2) + (width * height * 2);
      const deductedArea = (doors * 2.50) + (windows * 1.80);
      const totalOutput = totalArea - deductedArea;
      const totalLaborPrice = totalOutput * laborPrice;
      const totalPaint = totalOutput / 13;
      const totalPaint16L = Math.ceil(totalPaint / 16);

      document.getElementById('totalOutput').textContent = totalOutput.toFixed(2);
      document.getElementById('totalLaborPrice').textContent = totalLaborPrice.toFixed(2);
      document.getElementById('totalPaint').textContent = totalPaint.toFixed(2);
      document.getElementById('totalPaint16L').textContent = totalPaint16L;
    }
  </script>
</body>
</html>
