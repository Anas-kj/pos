import { Component, OnInit } from '@angular/core';
import { MessageService } from 'primeng/api';
import { EmployeeService } from '../services/employee/employee.service';
import { DynamicDialogRef } from 'primeng/dynamicdialog';
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

  constructor(
    private employeeService: EmployeeService,
    private messageService: MessageService,
    public ref: DynamicDialogRef
  ) {}

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
        entry.forceUpload = false;

        this.employeeService.upload(entry).subscribe(
          (data: BaseOut) => {
            const success = data.status_code === 201;
            const severity = success ? 'success' : 'error';
            this.messageService.add({severity, summary: severity, detail: data.detail});
            
            if(success){
              this.ref.close();
            }
        })
      }
    })
  }

}
