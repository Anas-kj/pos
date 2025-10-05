import { Component, OnInit } from '@angular/core';
import { Option } from 'src/libs/matchy/src/models/classes/option';
import { EmployeeService } from '../services/employee/employee.service';
import { ImportPossibleFields } from 'src/models/classes/importPossibleFields';
import { Matchy } from 'src/libs/matchy/src/main';
import { BaseOut } from 'src/models/interfaces/baseOut';
import { UploadEntry } from 'src/libs/matchy/src/models/classes/uploadEntry';
import { MatchyUploadEntry } from 'src/models/classes/matchyUploadEntry';

@Component({
  selector: 'app-import-employees',
  templateUrl: './import-employees.component.html',
  styleUrls: ['./import-employees.component.css']
})
export class ImportEmployeesComponent implements OnInit {

  constructor(private employeeService: EmployeeService) {

  }

  ngOnInit() {
    this.loadMatchyLib();
  }

  getOptions() {
    
  }

  loadMatchyLib(){
    this.employeeService.getOptions().subscribe((data: ImportPossibleFields) => {
      const matchy = new Matchy(data.possible_fields);

      document.getElementById('matchy')?.appendChild(matchy);

      matchy.submit = async (data: UploadEntry) => {
        const entry = new MatchyUploadEntry(data.lines, false);
        entry.forceUpload = true;

        this.employeeService.upload(entry).subscribe((data: BaseOut) => {
          alert('Employees imported successfully');
        })
      }
    })
  }

}
