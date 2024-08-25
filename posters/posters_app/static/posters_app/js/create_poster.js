// document.addEventListener('DOMContentLoaded', function () {
//     var formset = document.getElementById('image-formset');
//     var addButton = document.getElementById('add-form-row');
//     var totalForms = document.getElementById('id_form-TOTAL_FORMS');

//     addButton.addEventListener('click', function () {
//         var newForm = formset.querySelector('.form-row:last-child').cloneNode(true);
//         var formCount = parseInt(totalForms.value);
//         newForm.innerHTML = newForm.innerHTML.replace(/form-(\d+)-/g, 'form-' + formCount + '-');
//         formset.appendChild(newForm);
//         totalForms.value = formCount + 1;
//     });

//     formset.addEventListener('click', function (e) {
//         if (e.target.classList.contains('remove-form-row')) {
//             e.preventDefault();
//             e.target.parentNode.remove();
//             totalForms.value = parseInt(totalForms.value) - 1;
//         }
//     });
// });