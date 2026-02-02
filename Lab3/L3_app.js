const count = document.querySelector(".count");
const input = document.querySelector("input");

input.addEventListener("keyup", () => {
    count.innerHTML = input.value.length;
    
    // เพิ่มลูกเล่น: ถ้ามีตัวอักษรเปลี่ยนสีตัวเลขเป็นสีส้ม ถ้าว่างเปล่ากลับเป็นสีเดิม
    if (input.value.length > 0) {
        count.style.color = "#ff6b6b"; 
    } else {
        count.style.color = "#764ba2";
    }
});