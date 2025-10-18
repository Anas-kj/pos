import { Component, OnInit } from '@angular/core';
import { PrimeNGConfig, MenuItem } from 'primeng/api';

@Component({
  selector: 'app-main-layout',
  templateUrl: './main-layout.component.html',
  styleUrls: ['./main-layout.component.css']
})
export class MainLayoutComponent implements OnInit {
  menuBarItems: MenuItem[] | undefined;
  sidebarVisible = false;
  menuItems: MenuItem[] | undefined;

  constructor(private primengConfig: PrimeNGConfig) {}

  ngOnInit() {
    this.primengConfig.ripple = true;

    this.menuBarItems = [
      {
          label: '',
          icon: 'pi pi-bars',
          command: () => { this.sidebarVisible = !this.sidebarVisible; }
      },  
      {
          label: 'Quit',
          icon: 'pi pi-fw pi-power-off',
          styleClass: 'ml-auto',
      }
  ];

  this.menuItems = [
    {
        label: 'Employees',
        icon: 'pi pi-users',
        routerLink: '/employees'
    } 
  ];

  }
}
