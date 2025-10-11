import { Component, OnInit } from '@angular/core';
import { MessageService } from 'primeng/api';
import { EmployeeService } from '../services/employee/employee.service';
import { DynamicDialogRef } from 'primeng/dynamicdialog';
import { ImportPossibleFields } from 'src/models/classes/importPossibleFields';
import { Matchy } from 'src/libs/matchy/src/main';
import { UploadEntry } from 'src/libs/matchy/src/models/classes/uploadEntry';
import { MatchyUploadEntry } from 'src/models/classes/matchyUploadEntry';
import { MatchyWrongCells } from 'src/models/interfaces/matchyWrongCells';
import { importResponse } from 'src/models/interfaces/importResponse';

@Component({
  selector: 'app-import-employees',
  templateUrl: './import-employees.component.html',
  styleUrls: ['./import-employees.component.css']
})
export class ImportEmployeesComponent implements OnInit {
  warnings?: string;
  errors?: string;
  wrongCells?: MatchyWrongCells[] = [];

  constructor(
    private employeeService: EmployeeService,
    public messageService: MessageService,
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
          (data: importResponse) => {
            const success = data.status_code === 201;
            const severity = success ? 'success' : 'error';
            this.messageService.add({severity, summary: severity, detail: data.detail});
            
            if(success){
              this.ref.close();
            } else{
              this.warnings = data.warnings;
              this.errors = data.errors;
              this.wrongCells = data.wrong_cells;
              
              const patterns = [];
              const message_per_cell = new Map<string,string>();
              for(const cell of this.wrongCells!){
                const rowIndex = cell.rowIndex
                const colIndex = cell.colIndex
                
                patterns.push(`td[col="${colIndex}"][row="${rowIndex}"]`);
                message_per_cell.set(`${colIndex}, ${rowIndex}`, cell.message);
              }

              matchy.matchyQuerySelectorAll(patterns.join(', ')).forEach((htmlCell) => {
                const colIndex = htmlCell.getAttribute('col');
                const rowIndex = htmlCell.getAttribute('row');
                matchy.markInvalidCell(htmlCell, [message_per_cell.get(`${colIndex}, ${rowIndex}`)])
              }
            );
          }
        })
      }
    })
  }
}
