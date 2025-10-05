import { Component } from '@angular/core';
import { FormBuilder, FormGroup} from '@angular/forms';
import { EmployeeService } from '../services/employee/employee.service';
import { Gender, genders } from 'src/models/interfaces/enums/gender';
import { Validators } from '@angular/forms';
import { ContractType, contract_types } from 'src/models/interfaces/enums/contractType';
import { roles } from 'src/models/interfaces/enums/role';

@Component({
  selector: 'app-add-employee',
  templateUrl: './add-employee.component.html',
  styleUrls: ['./add-employee.component.css']
})
export class AddEmployeeComponent {
  employeeForm = this.fb.group({
    first_name: [null, Validators.required],
    last_name: [null],
    email: [null, [Validators.required, Validators.email]],
    number: [null, [Validators.required, Validators.min(1)]],
    birth_date: [null],
    address: [null],
    cnss_number: [null, [Validators.required, Validators.pattern("^\d{8}-\d{2}$")]],
    contract_type: [null],
    gender: [Gender.male],
    roles: [null],
    phone_number: [null],
    password: [null, Validators.required],
    confirm_password: [null, Validators.required],
  }, {
    validators: [this.passwordMatch(), this.requiredCnssNumber()]
  });;

  contractTypes: Object[];
  genders: Object[];
  roles: Object[];
  
  constructor(
    private employeeService: EmployeeService, 
    private fb: FormBuilder 
  ) {
    this.contractTypes = contract_types;
    this.genders = genders;
    this.roles = roles;
  }

  passwordMatch() {
    return (formGroup: FormGroup) => {
      const password = formGroup.controls['password'];
      const confirm_password = formGroup.controls['confirm_password'];

      if(confirm_password.errors && !confirm_password.errors['passwordMatch']) {
        return;
      }
      if(password.value !== confirm_password.value) {
        confirm_password.setErrors({ passwordMatch: true });
      } else {
        confirm_password.setErrors(null);
      }
    };
  }

  isEmptyString(str: string | undefined | null): boolean {
    return (str === '' || str == null);
  }


  requiredCnssNumber() {
    return (formGroup: FormGroup) => {
      const contract_type = formGroup.controls['contract_type'];
      const cnss_number = formGroup.controls['cnss_number'];

      if(cnss_number.errors && !cnss_number.errors['requiredCnssNumber']) {
        return;
      }
      if([ContractType.cdi, ContractType.cdd].includes(contract_type.value) && this.isEmptyString(cnss_number.value)) {
        cnss_number.setErrors({ requiredCnssNumber: true });
      } else {
        cnss_number.setErrors(null);
      }
    };
  }


}
