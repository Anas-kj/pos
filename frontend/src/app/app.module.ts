import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { EmployeesComponent } from './employees/employees.component';
import { AddEmployeeComponent } from './add-employee/add-employee.component';
import { EditEmployeeComponent } from './edit-employee/edit-employee.component';
import { DeleteEmployeeComponent } from './delete-employee/delete-employee.component';
import { ImportEmployeesComponent } from './import-employees/import-employees.component';
import { MessageService } from 'primeng/api';
import { MenubarModule } from 'primeng/menubar';
import { SidebarModule } from 'primeng/sidebar';
import { MenuModule } from 'primeng/menu';
import { TableModule } from 'primeng/table';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { DynamicDialogModule } from 'primeng/dynamicdialog';
import { InputNumberModule } from 'primeng/inputnumber';
import { CalendarModule } from 'primeng/calendar';
import { SelectButtonModule } from 'primeng/selectbutton';
import { DividerModule } from 'primeng/divider';
import { PasswordModule } from 'primeng/password';
import { ToastModule } from 'primeng/toast';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component'; 
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { LoginComponent } from './login/login.component';
import { ForgetPasswordComponent } from './forget-password/forget-password.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { ConfirmAccountComponent } from './confirm-account/confirm-account.component';

@NgModule({
  declarations: [
    AppComponent,
    EmployeesComponent,
    AddEmployeeComponent,
    EditEmployeeComponent,
    DeleteEmployeeComponent,
    ImportEmployeesComponent,
    PageNotFoundComponent,
    LoginComponent,
    ForgetPasswordComponent,
    ResetPasswordComponent,
    ConfirmAccountComponent,
  ],
  imports: [
    HttpClientModule,
    ReactiveFormsModule, 
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    SidebarModule,
    MenubarModule,
    MenuModule,
    TableModule,
    InputTextModule,
    ButtonModule,
    DynamicDialogModule,
    InputNumberModule,
    CalendarModule,
    SelectButtonModule,
    PasswordModule,
    DividerModule,
    ToastModule
  ],
  providers: [MessageService],
  bootstrap: [AppComponent]
})
export class AppModule { }
