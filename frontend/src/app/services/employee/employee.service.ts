import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { PagedResponse } from 'src/models/interfaces/pagedResponse';
import { EmployeeBase } from 'src/models/interfaces/employeeBase';
import { baseUrl } from 'src/models/baseUrl';
import { EmployeeFilter } from 'src/models/classes/employeeFilter';
import { EmployeeCreate } from 'src/models/interfaces/employeeCreate';

@Injectable({
  providedIn: 'root'
})

export class EmployeeService {
  constructor(private http: HttpClient) { }

  add(employee: EmployeeCreate) {
    const httpOptions = {}
    const endPointUrl = baseUrl + 'employee';
    return this.http.post(endPointUrl, employee, httpOptions);
  }

  getEmployees(employeeFilter: EmployeeFilter) {
    let params = new HttpParams()
      .set('name_substr', employeeFilter.name_substr as string)
      .set('page_size', employeeFilter.page_size)
      .set('page_number', employeeFilter.page_number);
    
    const httpOptions = {params}
    const endPointUrl = baseUrl + 'employee/all';
    return this.http.get<PagedResponse<EmployeeBase>>(endPointUrl, httpOptions);
  }
}