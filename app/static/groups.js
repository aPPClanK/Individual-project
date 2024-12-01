function openAttendance(studentId) {
    document.getElementById('overlay').style.display = 'block';
    fetch(`/groups/get_attendance?student_id=${studentId}`)
        .then(response => response.json())
        .then(data => {
            let attendanceTable = document.getElementById('attendance-table');
            
            // Очищаем таблицу перед добавлением новых данных
            attendanceTable.innerHTML = `
                <tr>
                    <th>Дата</th>
                    <th>Предмет</th>
                    <th>Статус</th>
                    <th>Оценка</th>
                </tr>
            `;

            if (data.length === 0) {
                // Если данных нет, показываем сообщение
                let emptyRow = `
                    <tr>
                        <td colspan="4" style="text-align:center;">Нет данных о посещаемости</td>
                    </tr>
                `;
                attendanceTable.innerHTML += emptyRow;
            } else {
                // Заполняем таблицу данными
                data.forEach(item => {
                    let row = `
                        <tr>
                            <td>${item[0]}</td>
                            <td>${item[1]}</td>
                            <td>${item[2]}</td>
                            <td>${item[3]}</td>
                        </tr>
                    `;
                    attendanceTable.innerHTML += row;
                });
            }
        })
        .catch(error => {
            console.error("Ошибка при получении данных о посещаемости:", error);
            // Показываем сообщение об ошибке
            let attendanceTable = document.getElementById('attendance-table');
            attendanceTable.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align:center; color:red;">Ошибка загрузки данных</td>
                </tr>
            `;
        });
}

// Функция для закрытия окна
function closeAttendance() {
    document.getElementById('overlay').style.display = 'none';
}
// Функция для открытия окна добавления группы
function openAddGroup() {
    document.getElementById('addGroupOverlay').style.display = 'block';
}
// Функция для закрытия окна добавления группы
function closeAddGroup() {
    document.getElementById('addGroupOverlay').style.display = 'none';
}
// Функция для открытия окна добавления студента
function openAddStudent() {
    document.getElementById('addStudentOverlay').style.display = 'block';
}
// Функция для закрытия окна добавления студента
function closeAddStudent() {
    document.getElementById('addStudentOverlay').style.display = 'none';
}
// Функция для подтверждения удаления
function confirmDelete(url) {
    if (confirm("Вы уверены, что хотите удалить это?")) {
        fetch(url, { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Ошибка при удалении.");
                }
            });
    }
}
function openEditStudent(studentId, firstName, lastName, dateOfBirth, gender, address, phone, email, studentGroupId) {
    document.getElementById('editStudentOverlay').style.display = 'block';
    document.getElementById('edit_student_id').value = studentId;
    document.getElementById('edit_first_name').value = firstName;
    document.getElementById('edit_last_name').value = lastName;
    document.getElementById('edit_date_of_birth').value = dateOfBirth;
    document.getElementById('edit_gender').value = gender;
    document.getElementById('edit_address').value = address;
    document.getElementById('edit_phone').value = phone;
    document.getElementById('edit_email').value = email;
    document.getElementById('edit_student_group_id').value = studentGroupId;
}

function closeEditStudent() {
    document.getElementById('editStudentOverlay').style.display = 'none';
}

function openEditGroup(groupId, groupName) {
    document.getElementById('edit_group_id').value = groupId;
    document.getElementById('edit_group_name').value = groupName;
    document.getElementById('editGroupOverlay').style.display = 'block';
}
function closeEditGroup() {
    document.getElementById('editGroupOverlay').style.display = 'none';
}