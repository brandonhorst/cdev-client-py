#!/usr/bin/env python3

import unittest
import cdev


class TestCDEVServer(unittest.TestCase):
    def setUp(self):
        self.instance = cdev.CacheInstance('bigfoot', 57776, '_SYSTEM', 'SYS')

    def get_samples(self):
        namespaces = self.instance.get_namespaces()
        self.assertIn('SAMPLES', [namespace.name for namespace in namespaces]) 

        samples = [namespace for namespace in namespaces if namespace.name == 'SAMPLES'][0]
        return samples

    def test_namespaces(self):
        self.get_samples()

    def test_queries(self):
        samples = self.get_samples()

        sql = "SELECT Name, SSN FROM Sample.Person"
        sqlresult = self.instance.add_query(samples, sql)
        self.assertTrue(sqlresult.success)
        self.assertIn(sql, sqlresult.query.content)

        executeresult = self.instance.execute_query(sqlresult.query)
        self.assertTrue(executeresult.success)
        self.assertIn("Name", executeresult.resultset)

    def test_globals(self):
        samples = self.get_samples()

        globs = self.instance.get_globals(samples)
        self.assertIn('oddDEF', [glob.name for glob in globs])

        personglob = [glob for glob in globs if glob.name == 'Sample.PersonD'][0]
        personglobfull = self.instance.get_global(personglob)
        self.assertIn('1', personglobfull.content)

    def test_classes_and_routines(self):
        samples = self.get_samples()

        files = self.instance.get_files(samples)
        self.assertIn('Sample.Person.cls', [file.name for file in files])
        self.assertIn('LDAP.mac', [file.name for file in files])

        personfile = [file for file in files if file.name == 'Sample.Person.cls'][0]
        person = self.instance.get_file(personfile)
        self.assertIn('Class Sample.Person', person.content)

        ldapfile = [file for file in files if file.name == 'LDAP.mac'][0]
        ldap = self.instance.get_file(ldapfile)
        self.assertIn('LDAP', ldap.content)

        person.content = '///modified by cdev\r\n{0}'.format(person.content)
        putmodifiedpersonrequest = self.instance.put_file(person)
        self.assertTrue(putmodifiedpersonrequest.success)

        ldap.content = '///modified by cdev\r\n{0}'.format(ldap.content)
        putmodifiedldaprequest = self.instance.put_file(ldap)
        self.assertTrue(putmodifiedldaprequest.success)

        newpersoncontent = person.content.replace('Sample.Person','Sample.CDEVPerson').replace('Stored_Procedure_Test','CDEV_Stored_Procedure_Test').replace('SP_Sample_By_Name','CDEV_Sample_By_Name')
        newpersonname = 'Sample.CDEVPerson.cls'
        newpersonresult = self.instance.add_file(samples, newpersonname, newpersoncontent)
        self.assertTrue(newpersonresult.success)

        newldapcontent = ldap.content
        newldapname = 'CDEVLDAP.mac'
        newldapresult = self.instance.add_file(samples, newldapname, newldapcontent)
        self.assertTrue(newldapresult.success)

        compilationresult = self.instance.compile_file(newpersonresult.file, 'ck')
        self.assertTrue(compilationresult.success)

        generatedfiles = self.instance.get_generated_files(compilationresult.file)
        self.assertIn('Sample.CDEVPerson.1.int', [file.name for file in generatedfiles])

        intfile = [file for file in generatedfiles if file.name == 'Sample.CDEVPerson.1.int'][0]
        int = self.instance.get_file(intfile)
        self.assertIn('Sample.CDEVPerson.1', int.content)

        personxml = self.instance.get_xml(person)
        self.assertIn('Sample.Person', personxml.content)

        personxmlresult = self.instance.put_xml(personxml)
        self.assertTrue(personxmlresult.success)
        self.assertEqual(personxmlresult.file.name, "Sample.Person.cls")

        anonxmlresult = self.instance.add_xml(samples, personxml.content)
        self.assertTrue(anonxmlresult.success)
        self.assertEqual(anonxmlresult.file.name, "Sample.Person.cls")

if __name__=='__main__':
    unittest.main()