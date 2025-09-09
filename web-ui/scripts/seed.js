const { PrismaClient } = require('@prisma/client')

const prisma = new PrismaClient()

async function seed() {
  try {
    console.log('Seeding database...')

    // Create default email templates
    const templates = [
      {
        name: 'Introduction Email',
        description: 'Initial outreach to new prospects',
        subject: 'Partnership Opportunity - Diksha Foundation',
        content: `Dear {{contact_person}},

I hope this email finds you well. I'm reaching out on behalf of Diksha Foundation to explore potential partnership opportunities with {{organization_name}}.

We believe there's strong alignment between our mission and your organization's commitment to {{focus_area}}.

Our organization has successfully trained over 2,500+ youth with an 85% employment rate, focusing on digital skills training and rural education access.

I would love to schedule a brief call to discuss how we might work together to create greater impact.

Best regards,
Diksha Foundation Team`,
        placeholders: ['contact_person', 'organization_name', 'focus_area'],
        type: 'INTRO',
        createdBy: 'system'
      },
      {
        name: 'Follow-up Email',
        description: 'Follow-up communications',
        subject: 'Following up on our partnership discussion',
        content: `Dear {{contact_person}},

I wanted to follow up on our recent discussion about potential partnership opportunities between Diksha Foundation and {{organization_name}}.

As mentioned, we have a strong track record in {{focus_area}} with measurable impact:
- 2,500+ youth trained
- 85% employment rate
- Focus on rural education access

I'm attaching our latest impact report for your review. Would you be available for a 30-minute call next week to discuss next steps?

Looking forward to hearing from you.

Best regards,
Diksha Foundation Team`,
        placeholders: ['contact_person', 'organization_name', 'focus_area'],
        type: 'FOLLOWUP',
        createdBy: 'system'
      },
      {
        name: 'Proposal Cover Email',
        description: 'Formal proposal submissions',
        subject: 'Partnership Proposal - Diksha Foundation',
        content: `Dear {{contact_person}},

Thank you for your interest in partnering with Diksha Foundation. I'm pleased to submit our formal partnership proposal for {{organization_name}}.

Our proposal outlines how we can work together to achieve mutual goals in {{focus_area}}, building on our proven track record of success.

Key highlights of our proposal:
- Collaborative approach to {{focus_area}}
- Measurable impact metrics
- Sustainable funding model
- Long-term partnership framework

I'm available to discuss any questions you may have about the proposal.

Best regards,
Diksha Foundation Team`,
        placeholders: ['contact_person', 'organization_name', 'focus_area'],
        type: 'PROPOSAL_COVER',
        createdBy: 'system'
      }
    ]

    for (const template of templates) {
      await prisma.emailTemplate.upsert({
        where: { name: template.name },
        update: template,
        create: template
      })
    }

    console.log('Email templates seeded successfully')

    // Create default admin user if none exists
    const adminUser = await prisma.user.findFirst({
      where: { role: 'ADMIN' }
    })

    if (!adminUser) {
      console.log('No admin user found. Please create one manually or promote an existing user.')
    }

    console.log('Database seeding completed successfully')
  } catch (error) {
    console.error('Seeding failed:', error)
    throw error
  } finally {
    await prisma.$disconnect()
  }
}

// Run seed if called directly
if (require.main === module) {
  seed()
    .catch((error) => {
      console.error(error)
      process.exit(1)
    })
}

module.exports = { seed }

