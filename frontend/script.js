const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadContent = document.getElementById('upload-content');
const previewContainer = document.getElementById('image-preview-container');
const previewImg = document.getElementById('preview-img');
const removeBtn = document.getElementById('remove-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const loading = document.getElementById('loading');
const resultSection = document.getElementById('result-section');

let currentFile = null;

// Handle Drag & Drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-active'), false);
});
['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-active'), false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
});

fileInput.addEventListener('change', function() {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        currentFile = files[0];
        
        // Cập nhật Preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            uploadContent.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            resultSection.classList.add('hidden'); // Ẩn kết quả cũ nếu có
        }
        reader.readAsDataURL(currentFile);
    }
}

removeBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    previewImg.src = '';
    uploadContent.classList.remove('hidden');
    previewContainer.classList.add('hidden');
    resultSection.classList.add('hidden');
});

analyzeBtn.addEventListener('click', async () => {
    if(!currentFile) return;

    // Hiển thị loading state
    previewContainer.classList.add('hidden');
    loading.classList.remove('hidden');
    
    // Gửi Form Data tới server API
    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        // Ẩn Loading
        loading.classList.add('hidden');
        previewContainer.classList.remove('hidden'); // Trả lại preview
        
        if(data.success) {
            showResult(data);
        } else {
            alert('Lỗi: ' + (data.message || 'Từ Backend Server!'));
        }

    } catch(err) {
        console.error(err);
        loading.classList.add('hidden');
        previewContainer.classList.remove('hidden');
        alert('Lỗi kết nối tới Server. Đảm bảo Backend đang chạy.');
    }
});

function showResult(data) {
    resultSection.classList.remove('hidden');
    document.getElementById('sys-msg').innerText = '';
    
    document.getElementById('confidence-score').innerText = data.confidence;

    if (data.food_data) {
        document.getElementById('food-name').innerText = data.food_data.name;
        document.getElementById('food-desc').innerText = data.food_data.description || 'Chưa có thông tin mô tả chi tiết.';
        document.getElementById('val-cal').innerText = data.food_data.calories;
        document.getElementById('val-prot').innerText = data.food_data.proteins;
        document.getElementById('val-carb').innerText = data.food_data.carbs;
        document.getElementById('val-fat').innerText = data.food_data.fats;
        
        // Hiển thị Công thức & Nguyên liệu
        const recipeContainer = document.getElementById('recipe-container');
        const ingredientsList = document.getElementById('ingredients-list');
        const recipeInstructions = document.getElementById('recipe-instructions');
        const recipeTime = document.getElementById('recipe-time');
        
        if (data.food_data.recipe_instructions || (data.food_data.ingredients && data.food_data.ingredients.length > 0)) {
            recipeContainer.classList.remove('hidden');
            
            // Xóa cũ
            ingredientsList.innerHTML = '';
            
            if (data.food_data.ingredients && data.food_data.ingredients.length > 0) {
                data.food_data.ingredients.forEach(item => {
                    const li = document.createElement('li');
                    li.innerText = `${item.TenNguyenLieu} - ${item.SoLuong}`;
                    ingredientsList.appendChild(li);
                });
            } else {
                ingredientsList.innerHTML = '<li>Đang cập nhật...</li>';
            }
            
            recipeInstructions.innerText = data.food_data.recipe_instructions || 'Đang cập nhật công thức làm món này...';
            
            if (data.food_data.recipe_time) {
                recipeTime.innerText = `(${data.food_data.recipe_time} phút)`;
            } else {
                recipeTime.innerText = '';
            }
        } else {
            // Không có
            recipeContainer.classList.add('hidden');
        }

    } else {
        // Model predict ra index hoặc tên nhưng trên Database SQLite chưa mapping data.
        document.getElementById('food-name').innerText = `${data.predicted_class_name}`;
        document.getElementById('food-desc').innerText = 'Dữ liệu sơ bộ từ AI (Chưa có record ánh xạ món ăn này trong Database).';
        document.getElementById('sys-msg').innerText = data.message;
        
        ['val-cal', 'val-prot', 'val-carb', 'val-fat'].forEach(id => {
            document.getElementById(id).innerText = '--';
        });
        document.getElementById('recipe-container').classList.add('hidden');
    }
}
