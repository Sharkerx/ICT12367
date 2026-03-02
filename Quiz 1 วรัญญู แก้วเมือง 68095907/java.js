// เลือก element จาก DOM
const message = document.getElementById("message");
const charCount = document.getElementById("charCount");
const form = document.getElementById("feedbackForm");
const result = document.getElementById("result");

// Event: เมื่อพิมพ์ข้อความ (Real-time)
message.addEventListener("input", function () {
    let currentLength = message.value.length;
    charCount.textContent = currentLength;

    // ถ้าใกล้ครบ 200 ตัวอักษร เปลี่ยนสีเตือน
    if (currentLength >= 180) {
        charCount.style.color = "red";
    } else {
        charCount.style.color = "black";
    }
});

// Event: เมื่อกด Submit
form.addEventListener("submit", function (event) {
    event.preventDefault(); // ป้องกันรีเฟรชหน้า

    let text = message.value.trim();

    if (text.length === 0) {
        alert("กรุณากรอกข้อความก่อนส่ง");
        return;
    }

    // แสดงผลลัพธ์
    result.innerHTML = `
        <div class="alert alert-success">
            บันทึกข้อมูลเรียบร้อยแล้ว <br>
            จำนวนตัวอักษรทั้งหมด: ${text.length}
        </div>
    `;

    // รีเซ็ตฟอร์ม
    form.reset();
    charCount.textContent = 0;
});