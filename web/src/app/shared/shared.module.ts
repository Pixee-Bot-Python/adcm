// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AddingModule } from './add-component/adding.module';
import {
  ActionMasterComponent,
  BaseListDirective,
  ButtonSpinnerComponent,
  DialogComponent,
  ExportComponent,
  ImportComponent,
  IssueInfoComponent,
  ListComponent,
  MainInfoComponent,
  Much2ManyComponent,
  ServiceHostComponent,
  StatusComponent,
  StatusInfoComponent,
} from './components';
import { HolderDirective } from './components/hostmap/holder.directive';
import { SimpleTextComponent } from './components/tooltip';
import { ConfigurationModule } from './configuration/configuration.module';
import { DetailsModule } from './details/details.module';
import {
  DynamicDirective,
  HoverDirective,
  InfinityScrollDirective,
  MultiSortDirective,
  ScrollDirective,
} from './directives';
import { FormElementsModule } from './form-elements/form-elements.module';
import { MaterialModule } from './material.module';
import { BreakRowPipe, TagEscPipe } from './pipes';
import { StuffModule } from './stuff.module';

@NgModule({
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    StuffModule,
    FormElementsModule,
    ConfigurationModule,
    AddingModule,
    DetailsModule
  ],
  declarations: [
    DialogComponent,
    ListComponent,
    Much2ManyComponent,
    BreakRowPipe,
    HoverDirective,
    DynamicDirective,
    ButtonSpinnerComponent,
    ActionMasterComponent,
    ServiceHostComponent,
    TagEscPipe,
    IssueInfoComponent,
    SimpleTextComponent,
    BaseListDirective,
    StatusComponent,
    StatusInfoComponent,
    MainInfoComponent,
    ScrollDirective,
    HolderDirective,
    MultiSortDirective,
    ImportComponent,
    ExportComponent,
    InfinityScrollDirective
  ],
  entryComponents: [DialogComponent, ActionMasterComponent, IssueInfoComponent, IssueInfoComponent, StatusInfoComponent, SimpleTextComponent],
  exports: [
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
    StuffModule,
    FormElementsModule,
    ConfigurationModule,
    AddingModule,
    DetailsModule,
    DialogComponent,
    ListComponent,
    Much2ManyComponent,
    BreakRowPipe,
    HoverDirective,
    DynamicDirective,
    ButtonSpinnerComponent,
    ServiceHostComponent,
    TagEscPipe,
    BaseListDirective,
    StatusComponent,
    StatusInfoComponent,
    MainInfoComponent,
    ScrollDirective,
    ImportComponent,
    ExportComponent,
    InfinityScrollDirective
  ]
})
export class SharedModule {}
