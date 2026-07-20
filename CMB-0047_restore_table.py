
from IPython.display import display, HTML

display(HTML("""
<h2 style='color:orange;'>INTERACTIVE SKY MAP — TABLE RESTORED</h2>

<div id="aladin-lite-div" style="width:100%; height:600px;"></div>

<br>

<button id="fetchBtn" style="background:#ff9800;color:black;padding:10px;font-weight:bold;">
Fetch Galaxy
</button>

<input id="coordBox" value="53.1625 -27.791389" style="width:260px;padding:8px;">

<button id="findBtn" style="background:#4caf50;color:white;padding:10px;font-weight:bold;">
Find Galaxy
</button>

<div id="output" style="margin-top:10px;font-family:monospace;"></div>

<script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js"></script>

<script>
setTimeout(function(){

    if (typeof A === "undefined") {
        document.getElementById("output").innerHTML = "❌ Aladin failed to load";
        return;
    }

    window.aladin = A.aladin('#aladin-lite-div', {
        survey: "P/DSS2/color",
        target: "53.1625 -27.791389",
        fov: 0.03
    });

    let output = document.getElementById("output");

    // FETCH
    document.getElementById("fetchBtn").onclick = function(){
        let c = window.aladin.getRaDec();
        let val = c[0].toFixed(6) + " " + c[1].toFixed(6);
        document.getElementById("coordBox").value = val;
        output.innerHTML = "✔ Coordinates: " + val;
    };

    // FIND + REAL TABLE
    document.getElementById("findBtn").onclick = function(){

        let coords = document.getElementById("coordBox").value;
        output.innerHTML = "🔎 Querying SIMBAD...";

        let url = "https://simbad.u-strasbg.fr/simbad/sim-coo?Coord=" 
                  + encodeURIComponent(coords) 
                  + "&Radius=15s&output.format=VOTable";

        fetch(url)
        .then(r => r.text())
        .then(txt => {

            let parser = new DOMParser();
            let xml = parser.parseFromString(txt, "text/xml");

            let rows = xml.getElementsByTagName("TR");

            if (rows.length === 0){
                output.innerHTML = "❌ No objects found";
                return;
            }

            let html = "<table border='1' style='border-collapse:collapse;font-size:12px'>";
            html += "<tr><th>Name</th><th>RA</th><th>DEC</th><th>Type</th></tr>";

            for (let i = 0; i < Math.min(rows.length, 10); i++){
                let cols = rows[i].getElementsByTagName("TD");

                if (cols.length >= 4){
                    html += "<tr>";
                    html += "<td>" + cols[0].textContent + "</td>";
                    html += "<td>" + cols[1].textContent + "</td>";
                    html += "<td>" + cols[2].textContent + "</td>";
                    html += "<td>" + cols[3].textContent + "</td>";
                    html += "</tr>";
                }
            }

            html += "</table>";

            output.innerHTML = html;

        })
        .catch(err => {
            output.innerHTML = "❌ Query failed: " + err;
        });
    };

},1000);
</script>
"""))
