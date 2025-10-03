import { Component, OnInit } from '@angular/core';
import { EmployeeBase } from 'src/models/interfaces/employeeBase';
import { EmployeeService } from '../services/employee/employee.service';
import { FormBuilder } from '@angular/forms';
import { PagedResponse } from 'src/models/interfaces/pagedResponse';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { debounceTime } from 'rxjs';
import { EmployeeFilter } from 'src/models/classes/employeeFilter';
import { AddEmployeeComponent } from '../add-employee/add-employee.component';
import { ImportEmployeesComponent } from '../import-employees/import-employees.component';

@Component({
  selector: 'app-employees',
  templateUrl: './employees.component.html',
  styleUrls: ['./employees.component.css'],
  providers: [DialogService]
})
export class EmployeesComponent implements OnInit{
  employees!: EmployeeBase[];
  loading: boolean = true;
  activityValues: number[] = [0, 100];
  employeeFilter: EmployeeFilter;
  totalRecords: number = 0;
  ref: DynamicDialogRef | undefined;
  employeeFilterForm = this.fb.group({
    name_substr: [''],
  });;

  constructor(
    private employeeService: EmployeeService, 
    private fb: FormBuilder,
    public dialogService: DialogService  
  ) {

    this.employeeFilter = new EmployeeFilter();
    this.employeeFilterForm.valueChanges
      .pipe(debounceTime(500))
      .subscribe((data: any) => {
        this.onValueChanged(data)
        }
      )
  }

  ngOnInit() {
    this.loadEmployees();
  }

  onValueChanged(data ?: any){
    this.employeeFilter = new EmployeeFilter(data.name_substr);
    this.loadEmployees()
  }

  loadEmployees() {
    this.employeeService.getEmployees(this.employeeFilter).subscribe((res: PagedResponse<EmployeeBase>) => {
      this.employees = res.list;
      this.totalRecords = res.total_records;
      this.loading = false; 
    });
  }

  onPageChanged(event: any) {
    this.employeeFilter.page_number = event.page / event.rows + 1;
    this.employeeFilter.page_size = event.rows;
    this.loadEmployees();
  } 


  openAddEmployeeDialogue() {
    this.ref = this.dialogService.open(AddEmployeeComponent, {});
    this.ref.onClose.subscribe((data: any) => {
      this.loadEmployees();
    });
  }

  openImportEmployeesDialogue(){
    this.ref = this.dialogService.open(ImportEmployeesComponent, {});
    this.ref.onClose.subscribe((data: any) => {
      this.loadEmployees();
    });
  }

  ngOnDestroy() {
    if (this.ref) {
      this.ref.close();
    }
  }
}
