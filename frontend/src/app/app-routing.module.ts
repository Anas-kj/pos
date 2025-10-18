import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { EmployeesComponent } from './employees/employees.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { LoginComponent } from './login/login.component';
import { ForgetPasswordComponent } from './forget-password/forget-password.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { ConfirmAccountComponent } from './confirm-account/confirm-account.component';
import { canActivateRoute } from './services/guard/guard.service';
import { Role } from 'src/models/interfaces/enums/role';
import { MainLayoutComponent } from './main-layout/main-layout.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '',   redirectTo: '/login', pathMatch: 'full' },
  { path: '',
   component: MainLayoutComponent,
   children: [
      {
      path: 'employees', 
      component: EmployeesComponent, 
      canActivate: [canActivateRoute], 
      data: {permittedRoles: [Role.Admin, Role.Superuser]} 
      }
    ]
  },
  { path: 'forgetPassword', component: ForgetPasswordComponent },
  { path: 'resetPassword', component: ResetPasswordComponent },
  { path: 'confirmAccount', component: ConfirmAccountComponent },
  { path: '404', component: PageNotFoundComponent },
  { path: '**', redirectTo: "/404" },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
